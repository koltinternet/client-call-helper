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
