import React from 'react';

export const TestPage: React.FC = () => {
  console.log('🔍 TestPage rendered');
  
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">테스트 페이지</h1>
      <p>이 페이지가 보인다면 React 앱이 정상적으로 작동하고 있습니다.</p>
      <button 
        onClick={() => {
          console.log('🔍 Button clicked');
          fetch('http://localhost:8001/api/dashboard/stats', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          })
          .then(res => res.json())
          .then(data => console.log('🔍 API Response:', data))
          .catch(err => console.error('❌ API Error:', err));
        }}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        API 테스트
      </button>
    </div>
  );
};

