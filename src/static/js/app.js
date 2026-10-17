/* ===== Allegro 库管理软件 · 前端脚本（原型阶段：示例数据与基础交互） ===== */

// 标记当前激活的导航项
function setActiveNav() {
  const path = location.pathname.split('/').pop() || 'index.html';
  const map = {
    'index.html': 'nav-index',
    'db.html': 'nav-db',
    'files.html': 'nav-files',
    'models.html': 'nav-models',
    'env.html': 'nav-env',
    'git.html': 'nav-git'
  };
  const id = map[path];
  if (id) document.getElementById(id)?.classList.add('active');
}

// 模块A：真实数据状态（经后端 API 读取 Access）
let partsCache = [];      // 当前查询结果缓存（供编辑/删除定位）
let editingPn = null;     // 正在编辑的器件编号
let dbInfo = null;        // 数据库状态（/api/db/info）

// 示例数据：文件校验（模块B）——按目录分组
const sampleFiles = {
  footprint: [
    { name: 'R0603.dra',   size: '12.4 KB', norm: '符合',   dup: '无' },
    { name: 'R0603.psm',   size: '6.8 KB',  norm: '符合',   dup: '无' },
    { name: 'C0805.dra',   size: '12.1 KB', norm: '符合',   dup: '无' },
    { name: 'R0402.dra',   size: '11.9 KB', norm: '命名不符', dup: '有' }
  ],
  pad: [
    { name: 'r0_6x1_6.pad', size: '1.2 KB', norm: '符合', dup: '无' },
    { name: 'c2_0_d1_0.pad', size: '1.1 KB', norm: '符合', dup: '无' },
    { name: 'c1_0.pad',     size: '1.0 KB', norm: '符合', dup: '有' }
  ],
  flash: [
    { name: 'FLASH_C_2_2_1_5.fsm', size: '0.9 KB', norm: '符合', dup: '无' }
  ],
  schematic: [
    { name: 'RES0603.olb',   size: '3.1 KB', norm: '符合', dup: '无' },
    { name: 'CAP0805.olb',   size: '3.0 KB', norm: '符合', dup: '无' },
    { name: 'MCU_LQFP48.olb', size: '4.2 KB', norm: '符合', dup: '无' }
  ]
};
const fileDirs = ['footprint', 'pad', 'flash', 'schematic'];
let curFileDir = 'footprint';

// 示例数据：3D 检查（模块C）
const sampleModels = [
  { fp: 'R0603',    step: '0603.stp',    status: 'ok' },
  { fp: 'C0805',    step: '0805.stp',    status: 'ok' },
  { fp: 'LQFP48',   step: 'LQFP48.stp',  status: 'ok' },
  { fp: 'SOD123',   step: 'SOD123.stp',  status: 'ok' },
  { fp: 'JST_XH2',  step: '缺失',        status: 'missing' },
  { fp: 'R0402',    step: '缺失',        status: 'missing' }
];

// 示例数据：env 配置（模块D）
const sampleEnv = [
  { key: 'padpath',    value: '$HOME/pcblib/symbol/pad' },
  { key: 'psmpath',    value: '$HOME/pcblib/symbol/footprint' },
  { key: 'flashpath',  value: '$HOME/pcblib/symbol/flash' },
  { key: 'steppath',   value: '$HOME/pcblib/3d' }
];
const sampleBat = `@echo off
rem 自动配置 Allegro env 库路径（原型示例）
set CDS_LIB=D:\\my_workspace\\project\\allegroLibmm
echo 配置 padpath = %CDS_LIB%\\symbol\\pad
echo 配置 psmpath = %CDS_LIB%\\symbol\\footprint
echo 配置 flashpath = %CDS_LIB%\\symbol\\flash
echo 配置 steppath = %CDS_LIB%\\3d
echo 完成。`;

document.addEventListener('DOMContentLoaded', () => {
  setActiveNav();
  if (document.getElementById('partTable')) { loadDbInfo(); loadParts(); loadInitSql(); }
  if (document.getElementById('fileTable')) renderFiles();
  if (document.getElementById('modelTable')) renderModels();
  if (document.getElementById('envTable')) renderEnv();
  if (document.getElementById('gitConfigTable')) renderGit();
  if (document.getElementById('libDirTable')) loadConfig();
  initTabs();
});

// 模块A：读取数据库状态（驱动/库/表）
function loadDbInfo() {
  fetch('/api/db/info')
    .then(r => r.json())
    .then(d => {
      dbInfo = d;
      renderDbInfo();
    })
    .catch(() => { dbInfo = null; renderDbInfo(); });
}

function renderDbInfo() {
  const bar = document.getElementById('dbStatusBar');
  const init = document.getElementById('initCard');
  if (!bar) return;
  if (!dbInfo) { bar.style.display = 'block'; bar.innerHTML = '<b>❌</b> 后端不可达'; return; }
  const d = dbInfo;
  let html = '';
  if (!d.db_exists) {
    html = '<b>❌</b> 数据库文件不存在：<code>' + (d.db_path || '') + '</code>';
  } else if (!d.connected) {
    html = '<b>⚠️</b> 数据库连接失败：' + (d.error || '');
  } else if (!d.has_part_table) {
    html = '<b>⚠️</b> 数据库存在，但缺少 <code>PART_TABLE</code> 表（需先建表）';
  } else {
    html = '<b>✅</b> 数据库已连接 · 表：<code>' + (d.tables || []).join('</code>, <code>') + '</code>';
  }
  if (d.drivers && d.drivers.length) html += '<br>ODBC 驱动：<code>' + d.drivers.join('</code> / <code>') + '</code>';
  if (d.db_path) html += '<br>当前数据库路径：<code>' + d.db_path + '</code>';
  bar.innerHTML = html;
  bar.style.display = 'block';
  if (init) {
    init.style.display = (d.db_exists && d.connected && d.has_part_table) ? 'none' : 'block';
  }
  if (init && d.db_exists && !d.has_part_table) {
    const h = document.getElementById('initHint');
    if (h) h.textContent = '数据库存在但未建表。请在 Access 中打开 ' + (d.db_path || '') + ' 后执行以下 SQL：';
  } else if (init && !d.db_exists) {
    const h = document.getElementById('initHint');
    if (h) h.textContent = '数据库文件尚未创建。请在 Access 中新建数据库文件于：' + (d.db_path || '') + '，并执行以下 SQL 建表。';
  }
}

// 加载建表 SQL 到指引框
function loadInitSql() {
  fetch('/api/db/init-sql')
    .then(r => r.json())
    .then(d => { const b = document.getElementById('initSqlBox'); if (b && d.ok) b.textContent = d.sql; })
    .catch(() => {});
}
function copyInitSql() {
  const b = document.getElementById('initSqlBox');
  if (!b) return;
  navigator.clipboard.writeText(b.textContent).then(() => toast('SQL 已复制'), () => toast('复制失败，请手动选择复制'));
}

// 模块A：查询并渲染器件列表
function loadParts() {
  const s = document.getElementById('searchPn') ? document.getElementById('searchPn').value : '';
  const t = document.getElementById('searchType') ? document.getElementById('searchType').value : '全部类型';
  const type = (t === '全部类型') ? '' : t;
  fetch('/api/parts?search=' + encodeURIComponent(s) + '&type=' + encodeURIComponent(type))
    .then(r => r.json())
    .then(d => {
      if (!d.ok) { toast(d.error || '查询失败'); return; }
      partsCache = d.rows;
      renderParts(d.rows);
    })
    .catch(() => toast('加载器件列表失败'));
}

function renderParts(rows) {
  const tb = document.querySelector('#partTable tbody');
  if (!tb) return;
  const html = (rows || []).map(p => `
    <tr>
      <td>${p.Part_Number ?? ''}</td><td>${p.Value || p.MPN || ''}</td><td>${p.Tolerance ?? ''}</td><td>${p.Part_Type ?? ''}</td>
      <td>${p.Manufacturer ?? ''}</td><td>${p.MPN ?? ''}</td><td>${p.Description ?? ''}</td><td>${p.Symbol_Name ?? ''}</td>
      <td>${p.PCB_Footprint ?? ''}</td><td>${p.Step_Model ?? ''}</td><td>${p.Datasheet ?? ''}</td><td>${p.RoHS ?? ''}</td>
      <td>${p.Temp_Range ?? ''}</td><td>${p.Supplier ?? ''}</td><td>${p.Cost ?? ''}</td>
      <td><span class="tag ${p.Lifecycle === 'Active' ? 'tag-ok' : 'tag-warn'}">${p.Lifecycle ?? ''}</span></td>
      <td>${p.Remark ?? ''}</td>
      <td><a href="javascript:;" class="btn" onclick="editPart('${p.Part_Number}')">编辑</a>
          <a href="javascript:;" class="btn" onclick="delPart('${p.Part_Number}')">删除</a></td>
    </tr>`).join('');
  tb.innerHTML = html || '<tr><td colspan="18" class="empty">无器件数据（或尚未建表）</td></tr>';
}

// 模块B：渲染文件校验表（按当前目录）
function renderFiles() {
  const tb = document.querySelector('#fileTable tbody');
  const dirMap = { footprint: 'symbol/footprint', pad: 'symbol/pad', flash: 'symbol/flash', schematic: 'schematic' };
  const list = sampleFiles[curFileDir] || [];
  const html = list.map(f => `
    <tr>
      <td>${f.name}</td><td>${dirMap[curFileDir]}</td><td>${f.size}</td>
      <td><span class="tag ${f.norm==='符合'?'tag-ok':'tag-danger'}">${f.norm}</span></td>
      <td><span class="tag ${f.dup==='无'?'tag-ok':'tag-warn'}">${f.dup}</span></td>
    </tr>`).join('');
  tb.innerHTML = html || '<tr><td colspan="5" class="empty">无文件</td></tr>';
}

// 模块C：渲染3D检查表
function renderModels() {
  const tb = document.querySelector('#modelTable tbody');
  const html = sampleModels.map(m => `
    <tr>
      <td>${m.fp}</td><td>${m.step}</td>
      <td><span class="tag ${m.status==='ok'?'tag-ok':'tag-danger'}">${m.status==='ok'?'已关联':'缺失'}</span></td>
    </tr>`).join('');
  tb.innerHTML = html;
}

// 模块D：渲染 env 配置
function renderEnv() {
  const tb = document.querySelector('#envTable tbody');
  const html = sampleEnv.map(e => `
    <tr><td><code>${e.key}</code></td><td><code>${e.value}</code></td></tr>`).join('');
  tb.innerHTML = html;
  const pre = document.getElementById('batPreview');
  if (pre) pre.textContent = sampleBat;
}

// 示例数据：Git 远程同步（模块E）
const sampleGit = {
  type: 'GitHub', addr: 'https://github.com/user/allegro-lib.git', branch: 'main',
  status: [
    { op: '打包上传（push）', state: '已完成', time: '2026-10-16 15:30' },
    { op: '远程拉取（pull）', state: '已完成', time: '2026-10-15 09:12' }
  ]
};

// 模块E：渲染 git 配置与状态
function renderGit() {
  const ctb = document.querySelector('#gitConfigTable tbody');
  ctb.innerHTML = `
    <tr><td>远程仓库类型</td><td><code>${sampleGit.type}</code>（GitHub / 私有 GitLab 可选）</td></tr>
    <tr><td>远程地址</td><td><code>${sampleGit.addr}</code></td></tr>
    <tr><td>分支</td><td><code>${sampleGit.branch}</code></td></tr>`;
  const stb = document.querySelector('#gitStatusTable tbody');
  stb.innerHTML = sampleGit.status.map(s => `
    <tr><td>${s.op}</td><td><span class="tag tag-ok">${s.state}</span></td><td>${s.time}</td></tr>`).join('')
    || '<tr><td colspan="3" class="empty">暂无同步记录</td></tr>';
}

// Tab 切换：文件管理按目录联动；其余为高亮
function initTabs() {
  document.querySelectorAll('.tabs').forEach(group => {
    group.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => {
        group.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const dir = tab.dataset.dir;
        if (dir && typeof renderFiles === 'function') {
          curFileDir = dir;
          renderFiles();
        }
      });
    });
  });
}

// 删除器件：二次确认（需求 G1）→ 真实删除
function delPart(pn) {
  if (!window.confirm('确认删除器件「' + pn + '」？此操作不可撤销。')) return;
  fetch('/api/parts/' + encodeURIComponent(pn), { method: 'DELETE' })
    .then(r => r.json())
    .then(d => { toast(d.ok ? d.message : (d.error || '删除失败')); if (d.ok) loadParts(); })
    .catch(() => toast('删除失败（后端不可达）'));
}

// 编辑器件：从缓存定位并回填表单
function editPart(pn) {
  const p = partsCache.find(x => x.Part_Number === pn);
  openPartModal(p);
}

// 新增/编辑器件 模态框
const FORM_MAP = {
  f_pn: 'Part_Number', f_value: 'Value', f_tolerance: 'Tolerance', f_type: 'Part_Type',
  f_mfr: 'Manufacturer', f_mpn: 'MPN', f_desc: 'Description', f_sym: 'Symbol_Name',
  f_fp: 'PCB_Footprint', f_step: 'Step_Model', f_ds: 'Datasheet', f_rohs: 'RoHS',
  f_temp: 'Temp_Range', f_supplier: 'Supplier', f_cost: 'Cost', f_life: 'Lifecycle', f_remark: 'Remark'
};

function openPartModal(part) {
  editingPn = (part && part.Part_Number) || null;
  document.getElementById('partModalTitle').textContent = part ? ('编辑器件：' + part.Part_Number) : '新增器件';
  const box = document.getElementById('partModal');
  box.classList.add('show');
  Object.keys(FORM_MAP).forEach(id => {
    const field = FORM_MAP[id];
    const el = document.getElementById(id);
    if (el) el.value = (part && part[field] != null) ? part[field] : '';
  });
}
function closePartModal() {
  document.getElementById('partModal').classList.remove('show');
}
function savePart() {
  const part = {};
  Object.keys(FORM_MAP).forEach(id => { part[FORM_MAP[id]] = document.getElementById(id).value.trim(); });
  if (!part.Part_Number) { toast('器件编号（Part_Number）不能为空'); return; }
  const isNew = !editingPn;
  const url = isNew ? '/api/parts' : '/api/parts/' + encodeURIComponent(editingPn);
  const method = isNew ? 'POST' : 'PUT';
  fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(part) })
    .then(r => r.json())
    .then(d => {
      toast(d.ok ? d.message : (d.error || '保存失败'));
      if (d.ok) { closePartModal(); loadParts(); }
    })
    .catch(() => toast('保存失败（后端不可达）'));
}

// 占位动作：原型阶段按钮点击提示
window.toast = (msg) => alert('[原型] ' + msg);

/* ===== A3：导出 CSV 模板（直接下载，不跳转页面） ===== */
function exportTemplate() {
  window.location.href = '/api/parts/template';
}

/* ===== A2：CSV 批量导入（浏览器原生选文件，上传后报告成功/跳过/逐行错误） ===== */
function importParts() {
  const inp = document.getElementById('importFile');
  if (!inp) { toast('未找到导入控件'); return; }
  inp.value = '';
  inp.click();
}

document.addEventListener('change', function (e) {
  if (!e.target || e.target.id !== 'importFile') return;
  const file = e.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append('file', file);
  fetch('/api/parts/import', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(d => {
      if (!d.ok) { alert('导入失败：' + d.error); return; }
      let msg = '导入完成：共 ' + d.total + ' 条，成功 ' + d.inserted + ' 条，跳过 ' + d.skipped + ' 条。';
      if (d.errors && d.errors.length) {
        msg += '\n\n跳过明细：\n' +
          d.errors.slice(0, 20).map(x => '第' + x.row + '行 ' + x.part + '：' + x.msg).join('\n');
        if (d.errors.length > 20) msg += '\n…等共 ' + d.errors.length + ' 条';
      }
      alert(msg);
      loadParts();
    })
    .catch(() => toast('导入失败（后端不可达）'));
});

/* ===== G4：库根目录配置 ===== */
const DIR_LABEL = {
  database: 'CIS 数据库', schematic: '原理图符号', footprint: 'PCB 封装',
  pad: '焊盘', flash: '花焊盘', mech: '机械符号', model3d: '3D 模型', doc: '数据手册'
};

function loadConfig() {
  fetch('/api/config')
    .then(r => r.json())
    .then(cfg => {
      const inp = document.getElementById('libRootInput');
      if (inp) inp.value = cfg.lib_root;
      const dbin = document.getElementById('dbFileInput');
      if (dbin) dbin.value = cfg.db_file || '';
      const sub = document.getElementById('pageSub');
      if (sub) sub.textContent = '单机 · 约 300~500 器件 · 库根：' + cfg.lib_root;
      renderLibDirs(cfg);
    })
    .catch(() => toast('加载库根配置失败'));
}

function renderLibDirs(cfg) {
  const tb = document.querySelector('#libDirTable tbody');
  if (!tb) return;
  tb.innerHTML = Object.keys(cfg.subdirs).map(k => `
    <tr>
      <td>${DIR_LABEL[k] || k}</td>
      <td><code>${cfg.subdirs[k].path}</code></td>
      <td><span class="tag ${cfg.subdirs[k].exists ? 'tag-ok' : 'tag-warn'}">${cfg.subdirs[k].exists ? '存在' : '缺失'}</span></td>
    </tr>`).join('');
  const hint = document.getElementById('dbPathHint');
  if (hint) hint.textContent = 'CIS 数据库路径：' + cfg.db_path;
}

function saveLibRoot() {
  const v = document.getElementById('libRootInput').value.trim();
  const st = document.getElementById('cfgStatus');
  fetch('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lib_root: v })
  })
    .then(r => r.json())
    .then(res => {
      if (res.ok) {
        st.textContent = '✅ ' + res.message;
        st.className = 'cfg-status ok';
        const sub = document.getElementById('pageSub');
        if (sub) sub.textContent = '单机 · 约 300~500 器件 · 库根：' + res.config.lib_root;
        renderLibDirs(res.config);
      } else {
        st.textContent = '❌ ' + res.message;
        st.className = 'cfg-status err';
      }
    })
    .catch(() => { st.textContent = '❌ 保存失败（后端不可达）'; st.className = 'cfg-status err'; });
}

// G5：保存数据库文件路径（空串 = 恢复按库根推导）
function saveDbFile() {
  const v = document.getElementById('dbFileInput').value.trim();
  const st = document.getElementById('dbFileStatus');
  fetch('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ db_file: v })
  })
    .then(r => r.json())
    .then(res => {
      if (res.ok) {
        st.textContent = '✅ ' + res.message;
        st.className = 'cfg-status ok';
        renderLibDirs(res.config);
      } else {
        st.textContent = '❌ ' + res.message;
        st.className = 'cfg-status err';
      }
    })
    .catch(() => { st.textContent = '❌ 保存失败（后端不可达）'; st.className = 'cfg-status err'; });
}

// 数据库文件：打开系统文件选择对话框，选择后回填输入框
function browseDbFile() {
  const st = document.getElementById('dbFileStatus');
  st.textContent = '⏳ 请在弹出的窗口中选择数据库文件…';
  st.className = 'cfg-status';
  fetch('/api/config/browse-db')
    .then(r => r.json())
    .then(res => {
      if (res.ok && res.path) {
        document.getElementById('dbFileInput').value = res.path;
        st.textContent = '✅ 已选择，点击"保存数据库路径"生效';
        st.className = 'cfg-status ok';
      } else {
        st.textContent = (res.message || '未选择文件');
        st.className = 'cfg-status';
      }
    })
    .catch(() => { st.textContent = '❌ 打开文件对话框失败'; st.className = 'cfg-status err'; });
}

