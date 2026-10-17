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

// 示例数据：器件库（模块A）
// PART_TABLE 完整 17 字段示例数据（与《库管理规范》一致）
const sampleParts = [
  { pn:'R-0603-10K',   value:'10K',   tolerance:'±1%',   type:'电阻',   mfr:'Uniroyal',   mpn:'0603WAJ0102T5E', desc:'贴片电阻 10K 0603',         sym:'RES0603',    fp:'R0603',    step:'0603.stp',    ds:'doc/R-0603-10K.pdf',  rohs:'ROHS', temp:'-55~155℃',  supplier:'深圳华强北', cost:0.005, life:'Active',   remark:'常用上拉' },
  { pn:'R-0603-10K_S', value:'10K',   tolerance:'±1%',   type:'电阻',   mfr:'Uniroyal',   mpn:'0603WAJ0102T5E', desc:'贴片电阻 10K 0603 缩焊盘', sym:'RES0603',    fp:'R0603_S',  step:'0603.stp',    ds:'doc/R-0603-10K.pdf',  rohs:'ROHS', temp:'-55~155℃',  supplier:'深圳华强北', cost:0.005, life:'Active',   remark:'高密度用' },
  { pn:'C-0805-100N',  value:'100nF', tolerance:'±10%',  type:'电容',   mfr:'TDK',        mpn:'C1005X7R1H104K', desc:'贴片电容 100nF 0805',     sym:'CAP0805',    fp:'C0805',    step:'0805.stp',    ds:'doc/C-0805-100N.pdf',  rohs:'ROHS', temp:'-55~125℃',  supplier:'原厂代理',   cost:0.01,  life:'Active',   remark:'去耦' },
  { pn:'U-STM32F103',  value:'',      tolerance:'',      type:'MCU',    mfr:'ST',         mpn:'STM32F103C8T6',  desc:'ARM Cortex-M3 微控制器', sym:'MCU_LQFP48', fp:'LQFP48',   step:'LQFP48.stp',  ds:'doc/STM32F103.pdf',  rohs:'ROHS', temp:'-40~85℃',   supplier:'立创商城',   cost:8.5,   life:'Active',   remark:'主控' },
  { pn:'J-XH2-2P',     value:'',      tolerance:'',      type:'连接器', mfr:'JST',        mpn:'XH-2A',         desc:'2P 卧式 XH 连接器',     sym:'CON_XH2',    fp:'JST_XH2',  step:'—',           ds:'',                    rohs:'ROHS', temp:'-25~85℃',   supplier:'—',        cost:0.2,   life:'Active',   remark:'' },
  { pn:'D-SOD123-1N4148', value:'',   tolerance:'',      type:'二极管', mfr:'Nexperia',   mpn:'1N4148',        desc:'快恢复二极管 1N4148',   sym:'D_SOD123',   fp:'SOD123',   step:'SOD123.stp',  ds:'doc/1N4148.pdf',     rohs:'ROHS', temp:'-55~150℃',  supplier:'—',        cost:0.03,  life:'Obsolete', remark:'待淘汰' }
];

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
  if (document.getElementById('partTable')) renderParts();
  if (document.getElementById('fileTable')) renderFiles();
  if (document.getElementById('modelTable')) renderModels();
  if (document.getElementById('envTable')) renderEnv();
  if (document.getElementById('gitConfigTable')) renderGit();
  if (document.getElementById('libDirTable')) loadConfig();
  initTabs();
});

// 模块A：渲染器件表格
function renderParts() {
  const tb = document.querySelector('#partTable tbody');
  const html = sampleParts.map(p => `
    <tr>
      <td>${p.pn}</td><td>${p.value}</td><td>${p.tolerance}</td><td>${p.type}</td>
      <td>${p.mfr}</td><td>${p.mpn}</td><td>${p.desc}</td><td>${p.sym}</td>
      <td>${p.fp}</td><td>${p.step}</td><td>${p.ds}</td><td>${p.rohs}</td>
      <td>${p.temp}</td><td>${p.supplier}</td><td>${p.cost}</td>
      <td><span class="tag ${p.life==='Active'?'tag-ok':'tag-warn'}">${p.life}</span></td>
      <td>${p.remark}</td>
      <td><a href="javascript:;" class="btn" onclick="editPart('${p.pn}')">编辑</a> <a href="javascript:;" class="btn" onclick="delPart('${p.pn}')">删除</a></td>
    </tr>`).join('');
  tb.innerHTML = html;
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

// 删除器件：二次确认（需求 G1）
function delPart(pn) {
  if (window.confirm('确认删除器件「' + pn + '」？此操作不可撤销。')) {
    toast('器件已删除（原型，未写入数据库）：' + pn);
  }
}
function editPart(pn) {
  openPartModal();
  document.getElementById('partModalTitle').textContent = '编辑器件：' + pn;
}

// 新增/编辑器件 模态框（原型）
function openPartModal() {
  document.getElementById('partModal').classList.add('show');
  document.getElementById('partModalTitle').textContent = '新增器件';
}
function closePartModal() {
  document.getElementById('partModal').classList.remove('show');
}
function savePart() {
  closePartModal();
  toast('器件已保存（原型，未写入数据库）');
}

// 占位动作：原型阶段按钮点击提示
window.toast = (msg) => alert('[原型] ' + msg);

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
