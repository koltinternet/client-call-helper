<script>
    import { ActionMessage } from "./func/types";
    import { onMount } from "svelte";
    
    /** @type {WebSocket} */
    let socket = null;

    const ws_url = "ws:" + window.location.host + "/ws";
    
    /** @type ActionMessage[] */
    let actions = [{
        id: 1,
        phone: "89217809021",
        action: "new",
        status: "user",
        data: {}
    }];

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
            // Object.assign(message, { id : ++msg_id, data: {} });
            actions = [message, ...actions];
            return;
        }

        // Удаляем сообщение с завершённым событием из списка
        if (message.action === "done") {
            actions = actions.filter((action) => action.phone !== message.phone);
            return;
        }
        
        // Обновляем данные события, данными из Гидры
        if (message.action === "update") {
            const index = actions.findIndex((action) => action.phone === message.phone);
            Object.assign(actions[index], { data: message.data });

        } else {
            // Получаем индекс события, у которого аналогичный номер телефона
            const index = actions.findIndex((action) => action.phone === message.phone);
            // Обновляем событие
            Object.assign(actions[index], { action: message.action });
        }

        actions = [...actions];
        
    }

    // /**
    //  * Отправляет сообщение в ws.
    //  * @return {void}
    // */
    // function sendMsg() {
    //     if (!input_text) {
    //         return;
    //     }
    //     performMsg(input_text, username, false);

    //     socket.send(JSON.stringify({
    //         type: "message",
    //         data: {
    //             msg: input_text
    //         }
    //     }));

    //     input_text = "";
    //     audio_out.play();
    // }

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
            socket = new WebSocket(ws_url);

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


<div class="app-container">
    <h1>Активные события</h1>

    <hr>

    <div class="action-field">

        {#each actions as action (action.id)}
            <div class="action-item">
                <div class="action-type">{action.action}</div>
                <div class="action-body">
                    <div class="phone">{action.phone}</div>
                    <div class="status">{action.status}</div>
                </div>
            </div>
        {:else}
            <span class="empty">Пока нет активных событий</span>
        {/each}

    </div>
</div>


<style>
    .app-container {
        display: flex;
        flex-direction: column;
        gap: 10px;

        &> .action-field {
            min-height: 50px;
            
            &> .action-item {
                display: flex;
                gap: 10px;
                border: solid gray 1px;
                border-radius: 5px;
                padding: 10px;

                &> .action-type {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 150px;
                }

                &> .action-body {
                    display: flex;
                    flex-flow: row wrap;
                    gap: 5px;
                    width: 100%;

                    &> * {
                        padding: 5px;
                    }
                }
            }
        }
    }
</style>
