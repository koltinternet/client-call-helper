<script>
    import { ActionMessage } from "./lib/types";
    import { onMount } from "svelte";

    const chat_url = "ws:" + window.location.host + "/ws";

    /** @type ActionMessage[] */
    let actions = [];

    let msg_id = 0;
    
    // =============================================================

    /**
     * Обрабатывает сообщение, добавляя его в список сообщений,
     * если его action === "new" и удаляет, если action === "done",
     * иначе обновляет событие.
     * @param {ActionMessage} message - объект сообщения
     * @return {void}
    */
    function performMsg(message) {

        // Добавляем новое сообщение в список
        if (message.action === "new") {
            Object.assign(message, { id : ++msg_id, data: {} })
            actions = [message, ...actions];

        // Удаляем сообщение с завершённым событием из списка
        } else if (message.action === "done") {
            actions = actions.filter((action) => action.phone !== message.phone);
        
        // Обновляем данные событие
        } else if (message.action === "update") {
            const index = actions.findIndex((action) => action.phone === message.phone);
            Object.assign(actions[index], { data: message.data });
            actions = [...actions];
        } else {
            
            // Получаем индекс события, у которого аналогичный номер телефона
            const index = actions.findIndex((action) => action.phone === message.phone);
            // Обновляем событие
            Object.assign(actions[index], { action: message.action });
            actions = [...actions];
        }
        
    }

    /**
     * Отправляет сообщение в ws.
     * @return {void}
    */
    function sendMsg() {
        if (!input_text) {
            return;
        }
        performMsg(input_text, username, false);

        socket.send(JSON.stringify({
            type: "message",
            data: {
                msg: input_text
            }
        }));

        input_text = "";
        audio_out.play();
    }

    /**
     * Обработчик подключения к ws.
     * @param {Event} event
     * @return {void}
    */
    function handlerWSOpen(event) {
        socket.send(JSON.stringify({
            type: "join",
            data: {msg: ""}
        }))
    }

    /**
     * Обработчик получения сообщений.
     * @param {{data: string}} строка-JSON с сообщением
     * @return {void}
    */
    function handlerWSMessage({data}) {
        const msg = JSON.parse(data);
        performMsg(msg);
        console.log("Chat message: ", msg);
        // audio_in.play();
    }

    /**
     * Обработчик закрытия соединения.
     * @param {Event} event
     * @return {void}
    */
    function handlerWSClose(event) {
        console.log("Chat close: ", event);
    }

    /**
     * Обработчик ошибок соединения.
     * @param {Event} error
     * @return {void}
    */
    function handlerWSError(error) {
        console.log("Chat error: ", error);
    }

    /**
     * Создаёт подключение к ws.
     * @return {void}
    */
    function makeChat() {
        if (!socket || socket.readyState == WebSocket.CLOSED) {
            socket = new WebSocket(chat_url);

            socket.onopen = handlerWSOpen;
            socket.onmessage = handlerWSMessage;
            socket.onclose = handlerWSClose;
            socket.onerror = handlerWSError;
        }
    }

    onMount(() => {
        makeChat();
    });

</script>


<main>
    
</main>


<style>
    
</style>
