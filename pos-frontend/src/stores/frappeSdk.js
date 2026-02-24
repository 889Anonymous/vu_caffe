import { FrappeApp } from "frappe-js-sdk";

let host = window.location.hostname;
let protocol = window.location.protocol;
let url = `${protocol}//${host}:8000`;

export const frappe = new FrappeApp(url);

export default frappe;
