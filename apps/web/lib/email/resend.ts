import { Resend } from "resend";

export const RESEND_API_KEY = process.env.RESEND_API_KEY;
export const RESEND_FROM_EMAIL = process.env.RESEND_FROM_EMAIL || "hello@axorks.com";
export const NOTIFICATION_EMAIL = process.env.NOTIFICATION_EMAIL || "admin@axorks.com";

export const resend = new Resend(RESEND_API_KEY);
