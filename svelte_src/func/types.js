/**
 * @typedef {object} ActionMessageData
 * @property {number} id - идентификатор
 * @property {string} phone - номер телефона
 * @property {string} name - имя
 * @property {string} last_name - фамилия
 * @property {string} middle_name - отчество
 * @property {string} state - состояние абонента
 * @property {string} address - адрес
 */


/**
 * @typedef {object} ActionMessage
 * @property {number} id - идентификатор
 * @property {string} phone - номер телефона
 * @property {string} action - действие new|speak|done
 * @property {number} time - UNIX timestamp события
 * @property {string} status - статус user|forced|kvartira|chasny|...
 * @property {ActionMessageData} data - дополнительные данные
 */


const ActionMessage = {};

export {
    ActionMessage
};