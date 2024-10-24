<script>
    import { CallSession } from "./func/types";
    import { onMount } from "svelte";
    import { slide } from "svelte/transition";
    import HydraBtn from "./HydraBtn.svelte";
    
    /** @type {WebSocket} */
    let socket = null;

    const ws_url = "ws:" + window.location.host + "/ws";
    
    /** @type CallSession[] */
    let actions = [];

    let test_action = "welcome";

    const for_test = {
        phone: "+79217809021",
        action: "welcome",
        status: "toSupport",
        time: new Date(),
        event_id: "1729243964.366",
        support_id: "501",
        data: {
            login: "user",
            phone: "+79217809021",
            profile_url: "https://www.google.com/",
            full_name: "Вася Пупкин",
            short_name: "Пупкин В.",
            created_date: "2021-01-01 12:00:00",
            firm_id: 0,
            addresses: [{
                title: "Основной адрес",
                data: "г. Москва, ул. Льва Толстого, д. 16",
            }, {
                title: "Для связи",
                data: "+7 (495) 123-45-67",
            }],
        }
    };
    
    // =============================================================

    /**
     * Выполняет тестовый рендер события.
     * @return {void}
    */
    function handleTest() {
        actions = [for_test];
    }

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
        Alert.info(
            "WS-сервер подключился.",
            "Соединение установлено.",
            10
        )
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
        // console.log("WS close: ", event);
        Alert.warning(
            "WS-сервер закрыл соединение.<br>Пытаюсь переподключиться ...",
            "Соединение закрыто.",
        );
        retryWS();
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

    /**
     * Пытается повторить подключение к ws.
     * @return {void}
    */
    function retryWS() {
        socket = null;
        try {
            makeWS();
        } catch (error) {
            console.log(error);
        }
    }

    onMount(() => {
        retryWS();
    });

</script>


<div class="app-container">
    <h1>Активные события</h1>
    <div class="test">
        <button on:click={handleTest}>Тест</button>

        <select bind:value={test_action} on:change={() => {
            for_test.action = test_action;
        }}>
            <option value="welcome" selected>welcome</option>
            <option value="calling">calling</option>
            <option value="answered">answered</option>
        </select>
    </div>

    <hr>

    <div class="action-field">

        {#each actions as action (action.event_id)}
            <div transition:slide={{duration: 200, axis: "y"}}
                class="action-item"
                class:welcome={action.action === "welcome"}
                class:calling={action.action === "calling"}
                class:answered={action.action === "answered"}            
            >
                <div class="action-type">{action.status}</div>
                <div class="action-body">
                    <div class="phone">{action.phone}</div>
                    <!-- <div class="event-id">{action.event_id}</div> -->
                    <!-- <div class="status">{action.status}</div> -->

                    {#if action.data === null}
                        <div class="loading-data">Загрузка данных ...</div>

                    {:else}
                        {#if action.data.login === undefined}
                            <div class="empty-data">Неизвестный абонент</div>

                        {:else}
                            <div class="full-name">{action.data.full_name}</div>
                            <div class="addresses">

                                {#each action.data.addresses as address}
                                    <div class="address">
                                        <span class="address-title">{address.title}:</span>
                                        <span class="address-data">{address.data}</span>
                                    </div>
                                {/each}

                            </div>

                        {/if}
                        <div class="ceated">{new Date(action.time).toLocaleString()}</div>

                    {/if}

                </div>
                <div class="call-hydra" title="Открыть в Гидре"
                    role="button" tabindex="0" on:keypress={() => {}}
                    on:click={() => openNewWindow(action)}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="hydra-icon">
                        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                        <path d="M10 19a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z" />
                        <path d="M18 5a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z" />
                        <path d="M10 5a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z" />
                        <path d="M6 12a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z" />
                        <path d="M18 19a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z" />
                        <path d="M14 12a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z" />
                        <path d="M22 12a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z" />
                        <path d="M6 12h4" />
                        <path d="M14 12h4" />
                        <path d="M15 7l-2 3" />
                        <path d="M9 7l2 3" />
                        <path d="M11 14l-2 3" />
                        <path d="M13 14l2 3" />
                    </svg>
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
            display: flex;
            flex-direction: column;
            gap: 10px;
            
            &> .action-item {
                display: flex;
                gap: 10px;
                /* border: solid gray 1px; */
                box-shadow: none;
                border-radius: 5px;
                padding: 10px;
                background: transparent;
                transition: all 0.2s ease;

                &:hover {
                    box-shadow: 0 0 5px black;
                }

                &.clickable {
                    cursor: pointer;
                }

                &.welcome {
                    border: dashed rgba(128, 128, 128, 0.6) 1px;
                    background: rgba(128, 128, 128, 0.4);
                }

                &.calling {
                    border: solid orange 1px;
                    background: rgba(255, 165, 0, 0.4);
                }

                &.answered {
                    border: solid green 1px;
                    background: rgba(0, 128, 0, 0.4);
                }

                &> .action-type {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 150px;
                }

                &> .action-body {
                    display: grid;
                    grid-template:
                        "phone name ceated"
                        "addr  addr   addr"
                        / 1fr 1fr 1fr;
                    gap: 5px;
                    width: 100%;

                    &> * {
                        padding: 5px;
                    }

                    &> .phone {
                        grid-area: phone;
                    }

                    &> .full-name {
                        grid-area: name;
                    }

                    &> .ceated {
                        grid-area: ceated;
                    }

                    &> .addresses {
                        grid-area: addr;
                    }
                }

                &> .call-hydra {
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    color: black;

                    transition: all 0.2s ease;

                    &:hover {
                        color: red;
                    }

                    &> .hydra-icon {
                        transform: rotateZ(0deg);
                        transition: all 1s ease-in, all .2s ease-out;

                        &:hover {
                            transform: rotateZ(180deg);
                        }
                    }
                }
            }
        }
    }
</style>
