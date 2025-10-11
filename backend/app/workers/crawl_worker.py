# Celery worker tasks
from celery import current_task
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any
import json
from datetime import datetime, timezone, timedelta, date

from ..core.celery import celery_app
from ..core.database import sync_engine
from ..core.config import settings
from ..models import Keyword, Blog, KeywordTarget, CrawlRun, CrawlResult
from ..services.result_service import ResultService
from ..services.target_service import TargetService
from ..crawler.naver_crawler import crawl_keyword_async

# Create sync session maker for Celery
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

KST = timezone(timedelta(hours=9))


def kst_today() -> date:
    """Get today's date in KST"""
    return datetime.now(tz=KST).date()


def count_occurrences(parsed: List[Dict[str, Any]], url_pattern: str) -> tuple[int, str, str, str]:
    """Count occurrences of URL pattern in parsed results"""
    cnt = 0
    first_url = None
    first_title = None
    first_section = None
    
    for block in parsed:
        span = block.get("span")
        for box in block.get("article_boxes", []):
            for link in box.get("links", []):
                href = link.get("href", "")
                text = link.get("text", "")
                if href.startswith(url_pattern):
                    cnt += 1
                    if not first_url:
                        first_url = href
                        first_title = text
                        first_section = span
    
    return cnt, first_url, first_title, first_section


@celery_app.task(bind=True)
def crawl_keyword_task(self, keyword_id: int, blog_id: int):
    """Crawl a specific keyword for a specific blog"""
    db = SessionLocal()
    try:
        # Get keyword and blog
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        
        if not keyword or not blog:
            raise ValueError(f"Keyword {keyword_id} or Blog {blog_id} not found")
        
        # Get target mapping
        target = db.query(KeywordTarget).filter(
            KeywordTarget.keyword_id == keyword_id,
            KeywordTarget.blog_id == blog_id,
            KeywordTarget.is_active == True
        ).first()
        
        if not target:
            raise ValueError(f"No active target mapping for keyword {keyword_id} and blog {blog_id}")
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 1, "status": f"Crawling keyword: {keyword.keyword}"}
        )
        
        # Perform crawl
        parsed_results = crawl_keyword_async(keyword.keyword, settings.crawl_timeout_ms)
        snapshot_json = json.dumps(parsed_results, ensure_ascii=False)
        
        # Count occurrences
        cnt, first_url, first_title, section = count_occurrences(parsed_results, blog.url_pattern)
        
        # Save result
        result_service = ResultService(db)
        run_date = kst_today()
        
        crawl_result = result_service.create_crawl_result(
            keyword_id=keyword_id,
            blog_id=blog_id,
            keyword_target_id=target.id,
            found=(cnt > 0),
            occurrences=cnt,
            run_date=run_date,
            section=section,
            matched_url=first_url,
            matched_title=first_title,
            snapshot_json=snapshot_json if cnt > 0 else None
        )
        
        return {
            "status": "completed",
            "keyword_id": keyword_id,
            "blog_id": blog_id,
            "found": cnt > 0,
            "occurrences": cnt,
            "result_id": crawl_result.id
        }
        
    except Exception as exc:
        self.update_state(
            state="FAILURE",
            meta={"error": str(exc), "keyword_id": keyword_id, "blog_id": blog_id}
        )
        raise exc
    finally:
        db.close()


@celery_app.task(bind=True)
def crawl_all_keywords_task(self):
    """Crawl all active keyword-blog targets"""
    db = SessionLocal()
    try:
        # Create crawl run
        result_service = ResultService(db)
        crawl_run = result_service.create_crawl_run()
        
        # Get all active targets
        targets = db.query(KeywordTarget).filter(KeywordTarget.is_active == True).all()
        
        if not targets:
            return {"status": "completed", "message": "No active targets found"}
        
        total_targets = len(targets)
        success_count = 0
        fail_count = 0
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": total_targets, "status": "Starting crawl..."}
        )
        
        for i, target in enumerate(targets):
            try:
                # Update progress
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + 1,
                        "total": total_targets,
                        "status": f"Crawling {target.keyword.keyword} -> {target.blog.name}"
                    }
                )
                
                # Perform crawl
                parsed_results = crawl_keyword_async(target.keyword.keyword, settings.crawl_timeout_ms)
                snapshot_json = json.dumps(parsed_results, ensure_ascii=False)
                
                # Count occurrences
                cnt, first_url, first_title, section = count_occurrences(parsed_results, target.blog.url_pattern)
                
                # Save result
                run_date = kst_today()
                
                crawl_result = result_service.create_crawl_result(
                    keyword_id=target.keyword_id,
                    blog_id=target.blog_id,
                    keyword_target_id=target.id,
                    found=(cnt > 0),
                    occurrences=cnt,
                    run_date=run_date,
                    crawl_run_id=crawl_run.id,
                    section=section,
                    matched_url=first_url,
                    matched_title=first_title,
                    snapshot_json=snapshot_json if cnt > 0 else None
                )
                
                success_count += 1
                
            except Exception as e:
                fail_count += 1
                print(f"Error crawling {target.keyword.keyword} -> {target.blog.name}: {e}")
        
        # Update crawl run
        result_service.update_crawl_run(
            crawl_run.id,
            status="completed",
            finished_at=datetime.utcnow(),
            total_keywords=total_targets,
            success_count=success_count,
            fail_count=fail_count
        )
        
        return {
            "status": "completed",
            "run_id": crawl_run.id,
            "total_targets": total_targets,
            "success_count": success_count,
            "fail_count": fail_count
        }
        
    except Exception as exc:
        # Update crawl run with error
        if 'crawl_run' in locals():
            result_service.update_crawl_run(
                crawl_run.id,
                status="failed",
                finished_at=datetime.utcnow(),
                error_message=str(exc)
            )
        
        self.update_state(
            state="FAILURE",
            meta={"error": str(exc)}
        )
        raise exc
    finally:
        db.close()


@celery_app.task
def cleanup_old_results(days_to_keep: int = 90):
    """Clean up old crawl results"""
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old results
        deleted_count = db.query(CrawlResult).filter(
            CrawlResult.created_at < cutoff_date
        ).delete()
        
        # Delete old runs
        deleted_runs = db.query(CrawlRun).filter(
            CrawlRun.started_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return {
            "status": "completed",
            "deleted_results": deleted_count,
            "deleted_runs": deleted_runs
        }
        
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()

