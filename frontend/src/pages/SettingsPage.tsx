import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Settings, Bell, MessageSquare, Save, TestTube, Clock, Bot } from 'lucide-react';
import toast from 'react-hot-toast';

interface NotificationSettings {
  enabled: boolean;
  phone_number: string;
  notification_type: 'sms' | 'both';
  notify_on_success: boolean;
  notify_on_error: boolean;
}

interface ScheduleSettings {
  enabled: boolean;
  time: string;  // HH:MM 형식
  days: string[];  // ['monday', 'tuesday', ...]
}

interface AIBlogSettings {
  enabled: boolean;
  use_openai: boolean;  // true: OpenAI API, false: Mock
  model: string;
  temperature: number;
}

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<NotificationSettings>({
    enabled: false,
    phone_number: '',
    notification_type: 'sms',
    notify_on_success: true,
    notify_on_error: true,
  });

  const [isSaving, setIsSaving] = useState(false);
  
  const [scheduleSettings, setScheduleSettings] = useState<ScheduleSettings>({
    enabled: false,
    time: '09:00',
    days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
  });

  const [aiBlogSettings, setAIBlogSettings] = useState<AIBlogSettings>({
    enabled: false,
    use_openai: false,
    model: 'gpt-3.5-turbo',
    temperature: 0.7,
  });

  // 서버에서 설정 불러오기
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // 알림 설정 불러오기
        const notifResponse = await fetch('http://localhost:8001/api/settings/notifications', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (notifResponse.ok) {
          const data = await notifResponse.json();
          setSettings(data);
        }
        
        // 스케줄 설정 불러오기
        const scheduleResponse = await fetch('http://localhost:8001/api/settings/schedule', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (scheduleResponse.ok) {
          const data = await scheduleResponse.json();
          setScheduleSettings(data);
        }

        // AI 블로그 설정 불러오기
        const aiBlogResponse = await fetch('http://localhost:8001/api/settings/ai-blog', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (aiBlogResponse.ok) {
          const data = await aiBlogResponse.json();
          setAIBlogSettings(data);
        }
      } catch (error) {
        console.error('설정 불러오기 실패:', error);
      }
    };
    
    fetchSettings();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      const token = localStorage.getItem('token');
      const errors: string[] = [];
      
      // 알림 설정 저장
      const notifResponse = await fetch('http://localhost:8001/api/settings/notifications', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      });
      
      if (!notifResponse.ok) {
        errors.push('알림 설정');
      }
      
      // 스케줄 설정 저장
      const scheduleResponse = await fetch('http://localhost:8001/api/settings/schedule', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(scheduleSettings)
      });
      
      if (!scheduleResponse.ok) {
        errors.push('스케줄 설정');
      }

      // AI 블로그 설정 저장
      const aiBlogResponse = await fetch('http://localhost:8001/api/settings/ai-blog', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(aiBlogSettings)
      });
      
      if (!aiBlogResponse.ok) {
        errors.push('AI 블로그 설정');
      }
      
      // 결과 메시지
      if (errors.length === 0) {
        toast.success('✅ 모든 설정이 저장되었습니다!', {
          duration: 3000,
        });
      } else {
        toast.error(`❌ ${errors.join(', ')} 저장에 실패했습니다.`);
      }
    } catch (error) {
      console.error('설정 저장 오류:', error);
      toast.error('❌ 설정 저장 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestNotification = async () => {
    if (!settings.phone_number) {
      toast.error('전화번호를 입력해주세요.');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8001/api/settings/notifications/test', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
      } else {
        const data = await response.json();
        toast.error(data.detail || '테스트 메시지 전송에 실패했습니다.');
      }
    } catch (error) {
      toast.error('테스트 메시지 전송 중 오류가 발생했습니다.');
    }
  };

  const handlePhoneNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // 숫자만 입력되도록 필터링
    const value = e.target.value.replace(/[^0-9-]/g, '');
    setSettings(prev => ({ ...prev, phone_number: value }));
  };

  const handleDayToggle = (day: string) => {
    setScheduleSettings(prev => ({
      ...prev,
      days: prev.days.includes(day)
        ? prev.days.filter(d => d !== day)
        : [...prev.days, day]
    }));
  };

  const weekDays = [
    { value: 'monday', label: '월' },
    { value: 'tuesday', label: '화' },
    { value: 'wednesday', label: '수' },
    { value: 'thursday', label: '목' },
    { value: 'friday', label: '금' },
    { value: 'saturday', label: '토' },
    { value: 'sunday', label: '일' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">설정</h1>
          <p className="text-gray-600">알림 및 시스템 설정을 관리하세요</p>
        </div>
        {/* 전체 저장 버튼 - 상단 우측에 고정 */}
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={handleTestNotification}
            disabled={!settings.enabled || !settings.phone_number}
            className="flex items-center space-x-2"
          >
            <TestTube className="h-4 w-4" />
            <span>테스트 메시지</span>
          </Button>
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Save className="h-4 w-4" />
            <span>{isSaving ? '저장 중...' : '모든 설정 저장'}</span>
          </Button>
        </div>
      </div>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Bell className="h-5 w-5 text-gray-700" />
            <CardTitle>알림 설정</CardTitle>
          </div>
          <CardDescription>
            크롤링 완료 시 알림을 받을 방법을 설정하세요
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Enable Notifications */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">알림 활성화</label>
              <p className="text-sm text-gray-500">크롤링 완료 시 알림을 받습니다</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.enabled}
                onChange={(e) => setSettings(prev => ({ ...prev, enabled: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* Phone Number */}
          <div>
            <Input
              label="전화번호"
              type="tel"
              value={settings.phone_number}
              onChange={handlePhoneNumberChange}
              placeholder="010-1234-5678"
              disabled={!settings.enabled}
            />
            <p className="text-xs text-gray-500 mt-1">
              문자 메시지를 받을 전화번호를 입력하세요
            </p>
          </div>

          {/* Notification Type */}
          <div>
            <label className="text-sm font-medium text-gray-900 block mb-2">
              알림 방식
            </label>
            <div className="space-y-2">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="notification_type"
                  value="sms"
                  checked={settings.notification_type === 'sms'}
                  onChange={(e) => setSettings(prev => ({ ...prev, notification_type: 'sms' }))}
                  disabled={!settings.enabled}
                  className="text-blue-600"
                />
                <div>
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="h-4 w-4 text-gray-600" />
                    <span className="text-sm font-medium">SMS만</span>
                  </div>
                  <p className="text-xs text-gray-500">문자 메시지로만 알림을 받습니다</p>
                </div>
              </label>
            </div>
          </div>

          {/* Notification Triggers */}
          <div>
            <label className="text-sm font-medium text-gray-900 block mb-2">
              알림 조건
            </label>
            <div className="space-y-2">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notify_on_success}
                  onChange={(e) => setSettings(prev => ({ ...prev, notify_on_success: e.target.checked }))}
                  disabled={!settings.enabled}
                  className="rounded"
                />
                <div>
                  <span className="text-sm font-medium">크롤링 성공 시</span>
                  <p className="text-xs text-gray-500">크롤링이 성공적으로 완료되면 알림</p>
                </div>
              </label>
              
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notify_on_error}
                  onChange={(e) => setSettings(prev => ({ ...prev, notify_on_error: e.target.checked }))}
                  disabled={!settings.enabled}
                  className="rounded"
                />
                <div>
                  <span className="text-sm font-medium">크롤링 실패 시</span>
                  <p className="text-xs text-gray-500">크롤링이 실패하면 알림</p>
                </div>
              </label>
            </div>
          </div>

        </CardContent>
      </Card>

      {/* Schedule Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Clock className="h-5 w-5 text-gray-700" />
            <CardTitle>자동 크롤링 스케줄</CardTitle>
          </div>
          <CardDescription>
            매일 정해진 시간에 자동으로 크롤링을 실행합니다
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Enable Schedule */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">자동 크롤링 활성화</label>
              <p className="text-sm text-gray-500">매일 지정된 시간에 전체 크롤링을 실행합니다</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={scheduleSettings.enabled}
                onChange={(e) => setScheduleSettings(prev => ({ ...prev, enabled: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* Time */}
          <div>
            <Input
              label="실행 시간"
              type="time"
              value={scheduleSettings.time}
              onChange={(e) => setScheduleSettings(prev => ({ ...prev, time: e.target.value }))}
              disabled={!scheduleSettings.enabled}
            />
            <p className="text-xs text-gray-500 mt-1">
              매일 이 시간에 전체 크롤링이 실행됩니다 (서버 시간 기준)
            </p>
          </div>

          {/* Days */}
          <div>
            <label className="text-sm font-medium text-gray-900 block mb-2">
              실행 요일
            </label>
            <div className="flex space-x-2">
              {weekDays.map(day => (
                <button
                  key={day.value}
                  type="button"
                  onClick={() => handleDayToggle(day.value)}
                  disabled={!scheduleSettings.enabled}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    scheduleSettings.days.includes(day.value)
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  } ${!scheduleSettings.enabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  {day.label}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              선택된 요일: {scheduleSettings.days.length > 0 
                ? scheduleSettings.days.map(d => weekDays.find(w => w.value === d)?.label).join(', ')
                : '없음'}
            </p>
          </div>

          {/* Schedule Info */}
          {scheduleSettings.enabled && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">📅 스케줄 요약</h3>
              <p className="text-sm text-green-800">
                <strong>실행 시간:</strong> 매일 {scheduleSettings.time}
              </p>
              <p className="text-sm text-green-800">
                <strong>실행 요일:</strong> {scheduleSettings.days.map(d => weekDays.find(w => w.value === d)?.label).join(', ')}
              </p>
              <p className="text-sm text-green-800 mt-2">
                ℹ️ 다음 실행: {(() => {
                  const now = new Date();
                  const [hours, minutes] = scheduleSettings.time.split(':');
                  const nextRun = new Date();
                  nextRun.setHours(parseInt(hours), parseInt(minutes), 0, 0);
                  
                  if (nextRun <= now) {
                    nextRun.setDate(nextRun.getDate() + 1);
                  }
                  
                  return nextRun.toLocaleString('ko-KR');
                })()}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Blog Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Bot className="h-5 w-5 text-gray-700" />
            <CardTitle>🤖 AI 블로그 자동 작성</CardTitle>
          </div>
          <CardDescription>
            타겟 블로그가 검색 결과에 없을 때 AI가 자동으로 블로그 글을 생성합니다
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Enable AI Blog */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">AI 블로그 자동 생성</label>
              <p className="text-sm text-gray-500">타겟 블로그가 없을 때 자동으로 블로그 글을 생성합니다</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={aiBlogSettings.enabled}
                onChange={(e) => setAIBlogSettings(prev => ({ ...prev, enabled: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* Use OpenAI */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">OpenAI API 사용</label>
              <p className="text-sm text-gray-500">
                {aiBlogSettings.use_openai ? 'OpenAI GPT로 고품질 콘텐츠 생성' : 'Mock 데이터로 테스트 (무료)'}
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={aiBlogSettings.use_openai}
                onChange={(e) => setAIBlogSettings(prev => ({ ...prev, use_openai: e.target.checked }))}
                disabled={!aiBlogSettings.enabled}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>

          {/* Model Selection (OpenAI만) */}
          {aiBlogSettings.enabled && aiBlogSettings.use_openai && (
            <div>
              <label className="text-sm font-medium text-gray-900 block mb-2">
                AI 모델 선택
              </label>
              <select
                value={aiBlogSettings.model}
                onChange={(e) => setAIBlogSettings(prev => ({ ...prev, model: e.target.value }))}
                className="input"
              >
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo (빠름, 저렴)</option>
                <option value="gpt-4">GPT-4 (고품질, 비쌈)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                GPT-3.5: 빠르고 저렴 ($0.01-0.03/글) | GPT-4: 느리지만 고품질 ($0.30-0.50/글)
              </p>
            </div>
          )}

          {/* AI 설정 정보 */}
          {aiBlogSettings.enabled && (
            <div className={`p-4 border rounded-lg ${aiBlogSettings.use_openai ? 'bg-green-50 border-green-200' : 'bg-blue-50 border-blue-200'}`}>
              <h3 className={`font-semibold mb-2 ${aiBlogSettings.use_openai ? 'text-green-900' : 'text-blue-900'}`}>
                {aiBlogSettings.use_openai ? '🤖 OpenAI 모드' : '🧪 테스트 모드'}
              </h3>
              <div className={`text-sm space-y-1 ${aiBlogSettings.use_openai ? 'text-green-800' : 'text-blue-800'}`}>
                {aiBlogSettings.use_openai ? (
                  <>
                    <p><strong>모드:</strong> OpenAI API 사용</p>
                    <p><strong>모델:</strong> {aiBlogSettings.model}</p>
                    <p><strong>품질:</strong> 고품질 AI 생성 콘텐츠</p>
                    <p><strong>비용:</strong> 글 1개당 약 ${aiBlogSettings.model === 'gpt-4' ? '0.30-0.50' : '0.01-0.03'}</p>
                    <p className="mt-2 text-xs">
                      💡 .env 파일에 OPENAI_API_KEY 설정이 필요합니다
                    </p>
                  </>
                ) : (
                  <>
                    <p><strong>모드:</strong> Mock 테스트</p>
                    <p><strong>비용:</strong> 무료</p>
                    <p><strong>속도:</strong> 즉시 생성</p>
                    <p><strong>용도:</strong> 개발 및 테스트</p>
                    <p className="mt-2 text-xs">
                      💡 실제 운영 시에는 OpenAI API 사용을 권장합니다
                    </p>
                  </>
                )}
              </div>
            </div>
          )}

          {/* OpenAI 설정 가이드 */}
          {aiBlogSettings.enabled && aiBlogSettings.use_openai && (
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <h3 className="font-semibold text-purple-900 mb-2">🔧 OpenAI API 설정 방법</h3>
              <ol className="text-sm text-purple-800 space-y-2 list-decimal list-inside">
                <li><strong>OpenAI 계정</strong>: <a href="https://platform.openai.com" target="_blank" rel="noopener noreferrer" className="text-purple-600 underline">https://platform.openai.com</a></li>
                <li><strong>API Key 발급</strong>: API Keys 메뉴에서 "Create new secret key"</li>
                <li><strong>결제 수단 등록</strong>: Billing 메뉴에서 결제 수단 추가</li>
                <li><strong>.env 파일 설정</strong>:
                  <div className="mt-2 p-2 bg-purple-100 rounded font-mono text-xs">
                    OPENAI_API_KEY=sk-proj-xxxxx
                  </div>
                </li>
                <li><strong>서버 재시작</strong>: 설정 후 서버를 재시작하세요</li>
              </ol>
            </div>
          )}
        </CardContent>
      </Card>

      {/* SMS Provider Info */}
      {settings.enabled && (
        <Card>
          <CardHeader>
            <CardTitle>SMS 발송 정보</CardTitle>
            <CardDescription>
              문자 메시지 발송에 대한 안내
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">📱 알리고 SMS 연동</h3>
                <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
                  <li>알리고(smartsms.aligo.in)를 통해 SMS 발송</li>
                  <li>크롤링 완료/실패 시 자동으로 메시지 전송</li>
                  <li>전화번호는 서버에 안전하게 저장됩니다</li>
                </ul>
              </div>

              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <h3 className="font-semibold text-purple-900 mb-2">🔧 알리고 API 설정 방법</h3>
                <ol className="text-sm text-purple-800 space-y-2 list-decimal list-inside">
                  <li><strong>알리고 회원가입</strong>: <a href="https://smartsms.aligo.in" target="_blank" rel="noopener noreferrer" className="text-purple-600 underline">https://smartsms.aligo.in</a></li>
                  <li><strong>API Key 발급</strong>: 로그인 후 [API 연동] 메뉴에서 발급</li>
                  <li><strong>발신번호 등록</strong>: [발신번호 관리]에서 본인 인증 후 등록</li>
                  <li><strong>충전</strong>: SMS 발송을 위한 캐시 충전</li>
                  <li><strong>.env 파일 설정</strong>:
                    <div className="mt-2 p-2 bg-purple-100 rounded font-mono text-xs">
                      ALIGO_API_KEY=발급받은_API_KEY<br/>
                      ALIGO_USER_ID=알리고_아이디<br/>
                      ALIGO_SENDER=등록된_발신번호
                    </div>
                  </li>
                  <li><strong>서버 재시작</strong>: 설정 후 서버를 재시작하세요</li>
                </ol>
              </div>

              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h3 className="font-semibold text-yellow-900 mb-2">⚠️ 주의사항</h3>
                <ul className="text-sm text-yellow-800 space-y-1 list-disc list-inside">
                  <li>알리고 API 키가 설정되어 있어야 실제 발송됩니다</li>
                  <li>SMS 발송 시 건당 비용이 발생합니다 (약 15원/건)</li>
                  <li>전화번호 형식: 010-1234-5678 또는 01012345678</li>
                  <li>발신번호는 본인 인증된 번호만 사용 가능합니다</li>
                </ul>
              </div>

              {settings.phone_number && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h3 className="font-semibold text-green-900 mb-2">✅ 현재 설정</h3>
                  <div className="text-sm text-green-800 space-y-1">
                    <p><strong>전화번호:</strong> {settings.phone_number}</p>
                    <p><strong>알림 방식:</strong> {settings.notification_type === 'sms' ? 'SMS' : '이메일 + SMS'}</p>
                    <p><strong>성공 알림:</strong> {settings.notify_on_success ? '활성화' : '비활성화'}</p>
                    <p><strong>실패 알림:</strong> {settings.notify_on_error ? '활성화' : '비활성화'}</p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 하단 고정 저장 버튼 (스크롤해도 보이도록) */}
      <div className="sticky bottom-0 bg-gradient-to-t from-white via-white to-transparent pt-6 pb-4 -mx-8 px-8 mt-8">
        <div className="flex items-center justify-end space-x-3 max-w-5xl mx-auto">
          <Button
            variant="outline"
            onClick={handleTestNotification}
            disabled={!settings.enabled || !settings.phone_number}
            className="flex items-center space-x-2"
          >
            <TestTube className="h-4 w-4" />
            <span>테스트 메시지</span>
          </Button>
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white shadow-lg"
          >
            <Save className="h-4 w-4" />
            <span>{isSaving ? '저장 중...' : '모든 설정 저장'}</span>
          </Button>
        </div>
      </div>
    </div>
  );
};
