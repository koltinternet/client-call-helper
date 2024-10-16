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