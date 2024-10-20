# Client Call Helper

Создаёт сервер для запуска внутри локальной сети, ожидающий JSON-уведомления об активности телефонных сессий.

Сервер уведомляет все WS-соединения об изменении состояния телефонных сессий, попутно выполняя запрос к Гидре для получения данных об учётной записи, привязанной к номеру телефона.

## Установка

Клонировать этот репозиторий:
```shell
git clone https://github.com/koltinternet/client-call-helper.git
```

Запустить сценарий оболочки с именем `prepare`, в зависимости от операционной системы. Это создаст виртуальное окружение и установит зависимости.

### Окружение для разработки

Пользовательский интерфейс разрабатывается на Svelte.
> [!IMPORTANT]
> Для запуска компилятора Svelte, в системе должен быть установлен Node.js.

Выполнить команду:
```shell
npm create svelte@latest svelte
cd svelte
npm install
```
Это установит компилятор `Svelte` версии 4.+ и сборщик `Vite`.

Заменить содержимое конфига `vite.config.js` следующим:
```js
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte'; 
import path from 'path';

const project = "main-app";
const root_dir = path.resolve(import.meta.dirname, '..');

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [svelte()],

    build: {
        outDir: root_dir + '/static/js', // Указываем папку для сборки
        emptyOutDir: false,              // Очищать папку перед сборкой

        rollupOptions: {
            input: root_dir + `/svelte_src/${project}.js`,
            output: {
                entryFileNames: `${project}.js`, // Фиксированное имя файла сборки


                // Настройки для ассетов (включая CSS)
                assetFileNames: ({ name }) => {
                    if (name.endsWith('.css')) {
                        return `${project}.css`;  // Фиксированное имя для CSS файла
                    }
                    return '[name]-[hash][extname]';  // Стандартная настройка для остальных ассетов
                }
            }
        }
    },

    server: {
        middlewareMode: true,  // Перевод сервера в режим middleware
    },
});
```

Исходники собираются из папки `svelte_src`. Для этого, из расположения папки `svelte`, выполнить команду:
```shell
npm run build
```

## Запуск

Запустить соответствующий сценарий оболочки с именем `run`.
