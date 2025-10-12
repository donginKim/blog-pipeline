import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, parseISO, isValid } from 'date-fns';
import { ko } from 'date-fns/locale';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date, formatStr: string = 'yyyy-MM-dd HH:mm'): string {
  try {
    let dateObj: Date;
    
    if (typeof date === 'string') {
      // SQLite 시간 형식 처리 (YYYY-MM-DD HH:MM:SS)
      if (date.includes(' ') && !date.includes('T')) {
        dateObj = new Date(date.replace(' ', 'T'));
      } else {
        dateObj = parseISO(date);
      }
    } else {
      dateObj = date;
    }
    
    if (!isValid(dateObj)) {
      console.warn('Invalid date:', date);
      return date.toString();
    }
    
    return format(dateObj, formatStr, { locale: ko });
  } catch (error) {
    console.error('formatDate error:', error, date);
    return date?.toString() || 'Invalid Date';
  }
}

export function formatRelativeTime(date: string | Date): string {
  try {
    let dateObj: Date;
    
    if (typeof date === 'string') {
      // SQLite 시간 형식 처리 (YYYY-MM-DD HH:MM:SS)
      if (date.includes(' ') && !date.includes('T')) {
        dateObj = new Date(date.replace(' ', 'T'));
      } else {
        dateObj = parseISO(date);
      }
    } else {
      dateObj = date;
    }
    
    if (!isValid(dateObj)) {
      console.warn('Invalid date:', date);
      return date.toString();
    }
    
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
    
    if (diffInSeconds < 0) return '미래';
    if (diffInSeconds < 60) return '방금 전';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}분 전`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}시간 전`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}일 전`;
    
    return format(dateObj, 'yyyy-MM-dd', { locale: ko });
  } catch (error) {
    console.error('formatRelativeTime error:', error, date);
    return date?.toString() || 'Invalid Date';
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('ko-KR').format(num);
}

export function formatPercentage(value: number, total: number): string {
  if (total === 0) return '0%';
  return `${((value / total) * 100).toFixed(1)}%`;
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'running':
      return 'text-blue-600 bg-blue-100';
    case 'completed':
      return 'text-green-600 bg-green-100';
    case 'failed':
      return 'text-red-600 bg-red-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
}

export function getStatusText(status: string): string {
  switch (status.toLowerCase()) {
    case 'running':
      return '실행 중';
    case 'completed':
      return '완료';
    case 'failed':
      return '실패';
    default:
      return status;
  }
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: number | undefined;
  return (...args: Parameters<T>) => {
    if (timeout !== undefined) {
      clearTimeout(timeout);
    }
    timeout = window.setTimeout(() => func(...args), wait);
  };
}

export function generateChartColors(count: number): string[] {
  const colors = [
    '#3B82F6', // blue
    '#EF4444', // red
    '#10B981', // green
    '#F59E0B', // yellow
    '#8B5CF6', // purple
    '#06B6D4', // cyan
    '#84CC16', // lime
    '#F97316', // orange
    '#EC4899', // pink
    '#6B7280', // gray
  ];
  
  const result: string[] = [];
  for (let i = 0; i < count; i++) {
    result.push(colors[i % colors.length]);
  }
  return result;
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

export function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text);
  } else {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    return Promise.resolve();
  }
}

export function downloadJson(data: any, filename: string): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
