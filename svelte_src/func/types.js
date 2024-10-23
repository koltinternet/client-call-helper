/**
 * @typedef {object} HydraAddress
 * @property {string} data - данные адреса/контакта
 * @property {string} title - наименование
 */

/**
 * @typedef {object} HydraData
 * @property {string} login - логин пользователя
 * @property {string} phone - номер телефона
 * @property {string} profile_url - URL профиля в Гидре
 * @property {string} full_name - полное имя
 * @property {string} short_name - сокращенное имя
 * @property {string} created_date - дата регистрации
 * @property {number} firm_id - неизвестный параметр
 * @property {HydraAddress[]} addresses - адреса
 */

/**
 * @typedef {object} CallSession
 * @property {string} phone - номер телефона
 * @property {string} action - действие welcome|calling|answered
 * @property {string} status - статус user|forced|kvartira|chasny|...
 * @property {string} time - datetime
 * @property {string} event_id - ID события
 * @property {string} support_id - ID телефонного аппарата
 * @property {HydraData} data - данные пользователя из Hydra
 */


const CallSession = {};

export {
    CallSession
};