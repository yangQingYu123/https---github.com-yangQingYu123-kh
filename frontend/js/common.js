/**
 * 后端地址通过 API_BASE 配置
 */
const API_BASE = 'http://127.0.0.1:8000';
const TOKEN_KEY = 'emp_token';
const USER_KEY = 'emp_user';

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function saveToken(t) { localStorage.setItem(TOKEN_KEY, t); }
function clearToken() { localStorage.removeItem(TOKEN_KEY); }
function saveUser(u) { localStorage.setItem(USER_KEY, u); }
function getUser() { return localStorage.getItem(USER_KEY); }

/**
 * 统一封装 fetch 请求
 * @param {string} url - 接口路径，如 /api/employees
 * @param {object} options - { method, body, headers }
 * @param {boolean} auth - 是否需要携带 token，默认 true
 */
async function request(url, options = {}, auth = true) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (auth && getToken()) {
    headers['Authorization'] = 'Bearer ' + getToken();
  }

  const res = await fetch(API_BASE + url, { ...options, headers });
  let data = null;
  try { data = await res.json(); } catch (e) { data = null; }

  if (res.status === 401) {
    // token 失效或未登录：清状态并跳登录页
    clearToken();
    if (!location.pathname.endsWith('login.html')) {
      location.href = 'login.html';
    }
    throw new Error((data && data.msg) || '请先登录');
  }

  // 统一响应 { code, msg, data }
  if (data && typeof data === 'object' && 'code' in data) {
    if (data.code !== 0) {
      throw new Error(data.msg || '请求失败');
    }
    return data;
  }

  // 兜底：处理 422 等未走统一格式的响应
  if (!res.ok) {
    const detail = (data && (data.detail || data.msg)) || `HTTP ${res.status}`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data;
}

/** 退出登录 */
function logout() {
  clearToken();
  location.href = 'login.html';
}

/** 未登录拦截：在需要认证的页面顶部调用 guard() */
function guard() {
  if (!getToken()) {
    location.href = 'login.html';
    throw new Error('未登录');
  }
}

/** 格式化日期（兼容 YYYY-MM-DD 与 Date 对象） */
function fmtDate(d) {
  if (!d) return '-';
  if (typeof d === 'string') return d;
  const dt = new Date(d);
  const m = (dt.getMonth() + 1).toString().padStart(2, '0');
  const day = dt.getDate().toString().padStart(2, '0');
  return `${dt.getFullYear()}-${m}-${day}`;
}

/** 状态中文 + 样式类 */
function statusInfo(s) {
  return s === 'active' ? { text: '在职', cls: 'on' } : { text: '离职', cls: 'off' };
}
