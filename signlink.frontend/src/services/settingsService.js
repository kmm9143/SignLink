// settingsService.js
// Responsible for managing application settings (local + optional remote sync).
// Preserves defaults, provides subscription for changes, and helpers to get/update/reset.

const STORAGE_KEY = 'signlink:settings';
const REMOTE_ENDPOINT = '/api/settings'; // adjust if backend exists

const DEFAULTS = {
  theme: 'light',
  notificationsEnabled: true,
  language: 'en-US',
  autoUpdate: false,
  // add other app defaults here
};

class SettingsService {
  constructor() {
    this._listeners = new Set();
    this._settings = this._loadFromStorage();
  }

  // Load settings from localStorage and merge with defaults
  _loadFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { ...DEFAULTS };
      const parsed = JSON.parse(raw);
      return { ...DEFAULTS, ...parsed };
    } catch (err) {
      // If parsing fails, fall back to defaults
      console.error('Failed to load settings, using defaults', err);
      return { ...DEFAULTS };
    }
  }

  // Persist current settings to localStorage
  _saveToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this._settings));
    } catch (err) {
      console.error('Failed to save settings', err);
    }
  }

  // Notify subscribers of change
  _emit() {
    for (const cb of this._listeners) {
      try {
        cb(this.getAll());
      } catch (err) {
        // swallow listener errors
        console.error('Settings listener error', err);
      }
    }
  }

  // Public: get a copy of all settings
  getAll() {
    return { ...this._settings };
  }

  // Public: get a single setting by key with optional fallback
  get(key, fallback) {
    if (key in this._settings) return this._settings[key];
    if (fallback !== undefined) return fallback;
    return DEFAULTS[key];
  }

  // Public: set multiple settings at once
  setAll(partial) {
    if (!partial || typeof partial !== 'object') return;
    this._settings = { ...this._settings, ...partial };
    this._saveToStorage();
    this._emit();
  }

  // Public: update a single setting
  set(key, value) {
    this._settings = { ...this._settings, [key]: value };
    this._saveToStorage();
    this._emit();
  }

  // Public: reset to defaults (optionally keep overrides)
  reset(keepKeys = []) {
    const keep = Array.isArray(keepKeys) ? keepKeys : [];
    const preserved = {};
    for (const k of keep) {
      if (k in this._settings) preserved[k] = this._settings[k];
    }
    this._settings = { ...DEFAULTS, ...preserved };
    this._saveToStorage();
    this._emit();
  }

  // Public: subscribe to changes. Returns unsubscribe function.
  subscribe(callback) {
    if (typeof callback !== 'function') throw new TypeError('callback must be a function');
    this._listeners.add(callback);
    // immediately call with current state
    try {
      callback(this.getAll());
    } catch (err) {
      console.error('Error invoking settings subscriber', err);
    }
    return () => this._listeners.delete(callback);
  }

  // Optional: sync with remote server. Returns latest settings from server or null on failure.
  async fetchRemote() {
    try {
      const resp = await fetch(REMOTE_ENDPOINT, { credentials: 'include' });
      if (!resp.ok) throw new Error(`Failed to fetch settings: ${resp.status}`);
      const data = await resp.json();
      if (data && typeof data === 'object') {
        this.setAll(data);
        return this.getAll();
      }
      return null;
    } catch (err) {
      console.warn('Remote settings fetch failed', err);
      return null;
    }
  }

  // Optional: push local settings to remote server. Returns server response or null.
  async pushRemote() {
    try {
      const resp = await fetch(REMOTE_ENDPOINT, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this._settings),
      });
      if (!resp.ok) throw new Error(`Failed to push settings: ${resp.status}`);
      const data = await resp.json();
      return data;
    } catch (err) {
      console.warn('Remote settings push failed', err);
      return null;
    }
  }
}

const settingsService = new SettingsService();

export default settingsService;