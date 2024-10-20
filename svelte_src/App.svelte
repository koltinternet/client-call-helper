<script>
    import { CallSession } from "./func/types";
    import { onMount } from "svelte";
    
    /** @type {WebSocket} */
    let socket = null;

    const ws_url = "ws:" + window.location.host + "/ws";
    
    /** @type CallSession[] */
    let actions = [{
        phone: "+79217809021",
        action: "welcome",
        status: "user",
        time: new Date(),
        event_id: "1729243964.366",
        support_id: "501",
        data: {}
    }];

    // let msg_id = 0;
    
    // =============================================================

    // /**
    //  * Обрабатывает сообщение, добавляя его в список сообщений,
    //  * если его action === "new" и удаляет, если action === "done",
    //  * иначе обновляет событие.
    //  * @param {CallSession} message - объект сообщения
    //  * @return {void}
    // */
    // function performMsg(message) {

    //     // Добавляем новое сообщение в список
    //     if (message.action === "new") {
    //         Object.assign(message, { id : ++msg_id, data: {} });
    //         actions = [message, ...actions];
    //         return;
    //     }

    //     // Удаляем сообщение с завершённым событием из списка
    //     if (message.action === "done") {
    //         actions = actions.filter((action) => action.phone !== message.phone);
    //         return;
    //     }

    //     const index = actions.findIndex((action) => action.phone === message.phone);
    //     // Обновляем данные события, данными из Гидры
    //     if (message.action === "update") {
    //         Object.assign(actions[index], { data: message.data });
        
    //     // Обновляем тип события
    //     } else {
    //         Object.assign(actions[index], { action: message.action });
    //     }

    //     actions = [...actions];
        
    // }

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
        // socket.send(JSON.stringify({
        //     type: "join",
        //     data: {msg: ""}
        // }))
    }

    /**
     * Обработчик получения сообщений.
     * @param {{data: string}} строка-JSON с сообщением
     * @return {void}
    */
    function handlerWSMessage({data}) {
        const msg = JSON.parse(data);
        console.log("WS message: ", msg);
        actions = msg;
        // performMsg(msg);
        // audio_in.play();
    }

    /**
     * Обработчик закрытия соединения.
     * @param {Event} event
     * @return {void}
    */
    function handlerWSClose(event) {
        console.log("WS close: ", event);
    }

    /**
     * Обработчик ошибок соединения.
     * @param {Event} error
     * @return {void}
    */
    function handlerWSError(error) {
        console.log("WS error: ", error);
    }

    /**
     * Создаёт подключение к ws.
     * @return {void}
    */
    function makeWS() {
        if (!socket || socket.readyState == WebSocket.CLOSED) {
            socket = new WebSocket(ws_url);

            socket.onopen = handlerWSOpen;
            socket.onmessage = handlerWSMessage;
            socket.onclose = handlerWSClose;
            socket.onerror = handlerWSError;
        }
    }

    /**
     * Открывает новое окно в браузере.
     * @param {CallSession} action
     * @return {void}
    */
    function openNewWindow(action) {
        if (!action.data || action.data.profile_url === undefined) {
            return;
        }
        window.open(action.data.profile_url, '_blank');
    }

    onMount(() => {
        makeWS();
    });

</script>


<div class="app-container">
    <h1>Активные события</h1>

    <hr>

    <div class="action-field">

        {#each actions as action (action.event_id)}
            <div role="button" tabindex="0" on:keypress={() => {}}
                class="action-item" on:click={() => openNewWindow(action)}
                class:clickable={action.data !== null && action.data.login !== undefined}
                class:welcome={action.action === "welcome"}
                class:calling={action.action === "calling"}
                class:answered={action.action === "answered"}            
            >
                <div class="action-type">{action.action}</div>
                <div class="action-body">
                    <div class="phone">{action.phone}</div>
                    <div class="status">{action.status}</div>

                    {#if action.data === null}
                        <div class="loading-data">Загрузка данных ...</div>

                    {:else}
                        {#if action.data.login === undefined}
                            <div class="empty-data">Неизвестный абонент</div>

                        {:else}
                            <div class="data">{action.data.full_name}</div>
                            <div class="ceated">{new Date(action.time).toLocaleString()}</div>

                        {/if}

                    {/if}

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

                &.clickable {
                    cursor: pointer;
                }

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
