
/**
 * Отправка формы FormData методом POST, подставляя
 * CSRF токен в путь адреса.
 * Обновляет токен при запросах.
 * Возвращает object.property_name - с результатом, или
 * object.error_message - с описанием ошибки, если object.error === true
 * @param {string} url адрес запроса
 * @param {FormData} data данные формы
 * @return {object} */
async function csrfFiles(url, data) {
    url = url.replace(/\/*$/, "") + "/" + csrf_token;
    const requestData = {
        method: "POST",
        body: data
    };

    const resp = await fetch(url, requestData);

    if (resp.ok) {
        const result = await resp.json();
        csrf_token = result.token;
        
        if (result.error) {
            return result;
        } else {
            return result.data;
        }
    } else {
        return {
            "error": true,
            "error_message": await resp.text(),
            "status": resp.status
        }
    }
}


/**
 * Отправка текстовых данных формы методом POST.
 * @param {string} url - адрес запроса
 * @param {object} data - данные формы
 * @return {string} */
async function postFormUrlencoded(url, data) {
    const query = Object.keys(data).map(function(key){
        return encodeURIComponent(key) + '=' + encodeURIComponent(data[key]);
    }).join('&');

    const requestData = {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: query
    };

    const resp = await fetch(url, requestData);
    return await resp.text();
}


/**
 * Отправка JSON данных методом POST.
 * @param {string} url - адрес запроса
 * @param {object} data - данные
 * @return {object} */
async function postJson(url, data, method = "POST") {
    const requestData = {
        method,
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    };

    const resp = await fetch(url, requestData);

    if (resp.ok) {
        return await resp.json();
    } else {
        return {
            "error": true,
            "error_message": await resp.text(),
            "status": resp.status
        }
    }
}


/**
 * Отправка JSON данных методом POST, подставляя
 * CSRF токен в путь адреса.
 * Обновляет токен при запросах.
 * Возвращает либо обект с результатом, либо
 * объект с описанием ошибки.
 * @param {string} url - адрес запроса
 * @param {object} data - данные
 * @param {string} method - метод
 * @return {Object} */
async function csrfJson(url, data, method = "POST") {
    // ? Удаляем символы "/" в конце url
    url = url.replace(/\/*$/, "") + "/" + csrf_token;
    
    const result = await postJson(url, data, method);
    csrf_token = result.token;
    
    if (result.error) {
        return result;
    } else {
        return result.data;
    }
}
