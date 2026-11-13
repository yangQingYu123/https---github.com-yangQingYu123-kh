'use strict';

guard();
document.getElementById('who').textContent = '当前账号：' + (getUser() || 'admin');

const PAGE_SIZE = 10;
let currentPage = 1;
let totalCount = 0;

/* ---------- 列表加载 ---------- */
async function loadList() {
  const kw = document.getElementById('kw').value.trim();
  const dept = document.getElementById('deptFilter').value;
  const params = new URLSearchParams({
    page: currentPage,
    page_size: PAGE_SIZE,
  });
  if (kw) params.append('keyword', kw);
  if (dept) params.append('department', dept);

  try {
    const res = await request('/api/employees?' + params.toString());
    renderTable(res.data.items);
    totalCount = res.data.total;
    renderPagination();
  } catch (e) {
    toast(e.message, 'err');
  }
}

function renderTable(list) {
  const tb = document.getElementById('tbody');
  const empty = document.getElementById('empty');
  if (!list || list.length === 0) {
    tb.innerHTML = '';
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';
  tb.innerHTML = list.map(e => {
    const st = statusInfo(e.status);
    return `<tr>
      <td>${escapeHtml(e.emp_no)}</td>
      <td>${escapeHtml(e.name)}</td>
      <td>${escapeHtml(e.department)}</td>
      <td>${escapeHtml(e.position || '-')}</td>
      <td>${escapeHtml(e.phone || '-')}</td>
      <td>${fmtDate(e.hire_date)}</td>
      <td><span class="status ${st.cls}">${st.text}</span></td>
      <td>
        <button class="btn-sm btn-edit" onclick='editEmp(${e.id})'>编辑</button>
        <button class="btn-sm btn-del" onclick='delEmp(${e.id})'>删除</button>
      </td>
    </tr>`;
  }).join('');
}

function renderPagination() {
  const totalPage = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
  document.getElementById('pageInfo').textContent = `第 ${currentPage} / ${totalPage} 页 · 共 ${totalCount} 条`;
  document.getElementById('prevBtn').disabled = currentPage <= 1;
  document.getElementById('nextBtn').disabled = currentPage >= totalPage;
}

function changePage(delta) {
  currentPage += delta;
  if (currentPage < 1) currentPage = 1;
  loadList();
}

async function loadDepartments() {
  try {
    const res = await request('/api/employees/departments');
    const sel = document.getElementById('deptFilter');
    res.data.forEach(d => {
      const o = document.createElement('option');
      o.value = d; o.textContent = d;
      sel.appendChild(o);
    });
  } catch (e) { }
}

function openForm(id) {
  clearErrors();
  document.getElementById('formTitle').textContent = id ? '编辑员工' : '新增员工';
  document.getElementById('formMask').classList.add('show');
  if (!id) {
    ['f_id','f_emp_no','f_name','f_department','f_position','f_phone','f_hire_date'].forEach(id => {
      document.getElementById(id).value = '';
    });
    document.getElementById('f_status').value = 'active';
    document.getElementById('f_emp_no').readOnly = false;
  }
}

function closeForm() {
  document.getElementById('formMask').classList.remove('show');
}

async function editEmp(id) {
  try {
    const res = await request('/api/employees/' + id);
    const e = res.data;
    openForm(id);
    document.getElementById('f_id').value = e.id;
    document.getElementById('f_emp_no').value = e.emp_no;
    document.getElementById('f_emp_no').readOnly = true; // 编辑时工号不可改
    document.getElementById('f_name').value = e.name;
    document.getElementById('f_department').value = e.department;
    document.getElementById('f_position').value = e.position || '';
    document.getElementById('f_phone').value = e.phone || '';
    document.getElementById('f_hire_date').value = e.hire_date;
    document.getElementById('f_status').value = e.status;
  } catch (e) {
    toast(e.message, 'err');
  }
}

function validate() {
  clearErrors();
  let ok = true;
  const empNo = v('f_emp_no'), name = v('f_name'), dept = v('f_department');
  const phone = v('f_phone'), hd = v('f_hire_date');

  if (!empNo) { showErr('f_emp_no', '请输入工号'); ok = false; }
  if (!name.trim()) { showErr('f_name', '姓名不能为空'); ok = false; }
  if (!dept) { showErr('f_department', '请输入部门'); ok = false; }
  if (phone && (!/^\d{11}$/.test(phone))) { showErr('f_phone', '手机号必须为 11 位数字'); ok = false; }
  if (!hd) { showErr('f_hire_date', '请选择入职日期'); ok = false; }
  else if (isNaN(Date.parse(hd))) { showErr('f_hire_date', '日期格式不合法'); ok = false; }
  return ok;
}

async function save() {
  if (!validate()) return;
  const id = document.getElementById('f_id').value;
  const payload = {
    emp_no: v('f_emp_no'),
    name: v('f_name').trim(),
    department: v('f_department').trim(),
    position: v('f_position'),
    phone: v('f_phone'),
    hire_date: v('f_hire_date'),
    status: v('f_status'),
  };

  const btn = document.getElementById('saveBtn');
  btn.disabled = true;
  try {
    if (id) {
      await request('/api/employees/' + id, { method: 'PUT', body: JSON.stringify(payload) });
      toast('更新成功', 'ok');
    } else {
      await request('/api/employees', { method: 'POST', body: JSON.stringify(payload) });
      toast('新增成功', 'ok');
    }
    closeForm();
    loadList();
    loadDepartments();
  } catch (e) {
    toast(e.message, 'err');
  } finally {
    btn.disabled = false;
  }
}

async function delEmp(id) {
  if (!confirm('确定要删除这条员工记录吗？此操作不可恢复。')) return;
  try {
    await request('/api/employees/' + id, { method: 'DELETE' });
    toast('已删除', 'ok');
    // 若删除后当前页无数据，回到上一页
    const rows = document.getElementById('tbody').children.length;
    if (rows === 1 && currentPage > 1) currentPage--;
    loadList();
    loadDepartments();
  } catch (e) {
    toast(e.message, 'err');
  }
}

function v(id) { return document.getElementById(id).value.trim(); }
function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
function showErr(fieldId, msg) {
  const el = document.getElementById('e_' + fieldId);
  el.textContent = msg; el.style.display = 'block';
}
function clearErrors() {
  document.querySelectorAll('.field .hint').forEach(e => { e.style.display = 'none'; e.textContent = ''; });
}
let toastTimer;
function toast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + (type || '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2500);
}

loadDepartments();
loadList();
