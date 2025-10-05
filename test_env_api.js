const https = require('https');
const fs = require('fs');

// Читаем переменные окружения из .env файла
let API_KEY = null;
let MODEL = 'deepseek/deepseek-chat-v3.1:free';

try {
  const envContent = fs.readFileSync('.env', 'utf8');
  const lines = envContent.split('\n');

  lines.forEach(line => {
    const trimmed = line.trim();
    if (trimmed.startsWith('OPENROUTER_API_KEY=')) {
      API_KEY = trimmed.split('=')[1];
      console.log('✅ Найден OPENROUTER_API_KEY в .env файле');
    }
  });
} catch (e) {
  console.log('❌ Ошибка чтения .env файла:', e.message);
}

if (!API_KEY) {
  console.log('❌ OPENROUTER_API_KEY не найден в .env файле');
  console.log('📝 Добавьте строку: OPENROUTER_API_KEY=ваш_ключ_сюда');
  process.exit(1);
}

const postData = JSON.stringify({
  model: MODEL,
  messages: [{
    role: 'user',
    content: 'Привет! Объясни что такое "аналогия" простыми словами.'
  }],
  max_tokens: 100
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

console.log('🧪 Тестируем новый API ключ из .env файла...');
console.log(`🤖 Модель: ${MODEL}`);
console.log('💬 Тестовый запрос: объяснение слова "аналогия"\n');

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
        console.log('✅ УСПЕХ! Новый API ключ работает!');
        console.log(`🤖 Ответ от DeepSeek: ${response.choices[0].message.content.substring(0, 200)}...`);
        console.log('\n🎉 Готово к развертыванию на сервере!');
      } catch (e) {
        console.log('❌ Ошибка парсинга JSON:', e.message);
      }
    } else {
      console.log('❌ ОШИБКА с новым API ключом!');
      console.log('📄 Ответ сервера:', data);

      if (res.statusCode === 401) {
        console.log('\n💡 Возможные причины:');
        console.log('  • Недостаточно средств на балансе Open Router');
        console.log('  • Ключ снова попал в публичный доступ');
        console.log('  • Проблемы с аккаунтом Open Router');
      }
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Ошибка сети:', e.message);
});

req.write(postData);
req.end();
