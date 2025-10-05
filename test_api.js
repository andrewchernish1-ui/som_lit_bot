const https = require('https');
const fs = require('fs');

// Читаем API ключ из .env файла
let API_KEY = 'your_openrouter_api_key_here'; // fallback
try {
  const envContent = fs.readFileSync('.env', 'utf8');
  const lines = envContent.split('\n');
  lines.forEach(line => {
    if (line.startsWith('OPENROUTER_API_KEY=')) {
      API_KEY = line.split('=')[1].trim();
    }
  });
} catch (e) {
  console.log('⚠️  Не найден .env файл, использую fallback ключ');
}

const MODEL = 'deepseek/deepseek-chat-v3.1:free';

const postData = JSON.stringify({
  model: MODEL,
  messages: [{
    role: 'user',
    content: 'Привет! Скажи что-нибудь на русском языке.'
  }],
  max_tokens: 50
});

const options = {
  hostname: 'openrouter.ai',
  port: 443,
  path: '/api/v1/chat/completions',
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
    'HTTP-Referer': 'https://github.com/andrewchernish1-ui/som_lit_bot',
    'X-Title': 'Literary Assistant Bot',
    'Content-Length': Buffer.byteLength(postData)
  }
};

console.log('🧪 Тестируем Open Router API ключ...');
console.log(`🤖 Модель: ${MODEL}`);
console.log('💬 Сообщение: Привет! Скажи что-нибудь на русском языке.\n');

const req = https.request(options, (res) => {
  console.log(`📊 Статус код: ${res.statusCode}`);

  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    if (res.statusCode === 200) {
      try {
        const response = JSON.parse(data);
        console.log('✅ УСПЕХ! API работает!');
        console.log(`🤖 Ответ: ${response.choices[0].message.content}`);
      } catch (e) {
        console.log('❌ Ошибка парсинга JSON:', e.message);
      }
    } else {
      console.log('❌ ОШИБКА!');
      console.log('📄 Ответ сервера:', data);
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Ошибка запроса:', e.message);
});

req.write(postData);
req.end();
