/* Deterministic 41-second animation. No wall-clock or random visual state. */
(() => {
  'use strict';
  const duration = 41;
  const starts = [0, 8, 17, 23, 31, 35, 41];
  const orange = '#ff3c00', ink = '#111', gray = '#777970', blue = '#1769aa';
  const $ = id => document.getElementById(id);
  const esc = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  const text = (x, y, value, size = 36, color = ink, anchor = 'start', weight = 700) => `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" text-anchor="${anchor}" font-weight="${weight}">${esc(value)}</text>`;
  const rect = (x, y, w, h, fill = '#fff', stroke = ink, sw = 3) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  const line = (x1, y1, x2, y2, color = ink, width = 4, dash = '') => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}" ${dash ? `stroke-dasharray="${dash}"` : ''}/>`;
  const clamp = t => Math.max(0, Math.min(1, t));
  const ease = t => 1 - Math.pow(1 - clamp(t), 3);
  const group = (t, content) => { const a = ease(t / .45); return `<g opacity="${a}" transform="translate(0,${(1 - a) * 14})">${content}</g>`; };
  const check = (x, y, color = orange) => `<path d="M ${x} ${y} l 13 13 l 25 -29" stroke="${color}" stroke-width="6" fill="none"/>`;
  function display(x, y, state = 'off', t = 0, w = 350, h = 350) {
    const lit = state !== 'off';
    let s = rect(x, y, w, h, '#232625', '#232625', 3);
    s += rect(x + 18, y + 18, w - 36, h - 36, lit ? '#f6ead0' : '#363b39', 'none', 0);
    if (state === 'image' || state === 'animation') {
      s += rect(x + 18, y + 18, w - 36, h - 36, '#16272d', 'none', 0);
      s += text(x + 40, y + 65, 'RDK X5', 34, '#fff');
      s += line(x + 40, y + h - 60, x + w - 40, y + h - 60, '#537278', 2);
      const cx = x + w / 2 + (state === 'animation' ? Math.sin(t * 2) * 75 : 0);
      const cy = y + h - 95 - (state === 'animation' ? Math.abs(Math.sin(t * 2.2)) * 105 : 55);
      s += `<circle cx="${cx}" cy="${cy}" r="24" fill="${orange}" stroke="#ffbb8f" stroke-width="3"/>`;
    }
    return s;
  }
  function recap(t) {
    let s = text(0, 70, '通信原理', 44) + line(0, 95, 750, 95, ink, 5);
    s += text(0, 170, 'SCLK', 34, orange);
    let d = 'M 190 175';
    for (let i = 0; i < 6; i++) d += ` H ${190 + i * 85 + 15} V 130 H ${190 + i * 85 + 55} V 175 H ${190 + (i + 1) * 85}`;
    s += `<path d="${d}" stroke="${orange}" stroke-width="5" fill="none"/>`;
    const cursor = 190 + (t * .23 % 1) * 510;
    s += line(cursor, 120, cursor, 190, '#aaa', 2);
    s += text(0, 265, 'MOSI', 34, blue) + line(190, 255, 720, 255, blue, 5);
    for (let i = 0; i < 4; i++) s += rect(190 + ((t * .25 + i / 4) % 1) * 510, 246, 18, 18, blue, 'none', 0);
    s += text(0, 360, 'CS', 34) + text(190, 360, '选中设备', 38);
    s += text(1040, 70, '点亮 SPI 小屏幕', 44) + line(1040, 95, 1660, 95, orange, 5);
    s += display(1160, 125, t < 2 ? 'off' : 'image', 0, 330, 320);
    s += group(t - 3.2, check(1030, 494) + text(1090, 505, '原理 → 接线 → 显示', 36, orange));
    return s;
  }
  function node(t) {
    let s = rect(0, 60, 800, 350, '#202624', '#202624', 3);
    s += text(35, 115, '终端 · 检查设备节点', 30, '#a9b7ad');
    s += text(35, 193, '$ ls /dev/spidev1.1', 39, '#fff');
    s += text(35, 272, t < 5.8 ? 'No such file or directory' : '/dev/spidev1.1', t < 5.8 ? 35 : 42, t < 5.8 ? '#ffb998' : '#a4e6b6');
    s += text(35, 360, t < 5.8 ? '先检查配置，再重新确认' : '节点出现后，继续显示测试', 31, '#d7ded8');
    const steps = [['01', '开启 SPI1', 'sudo srpi-config'], ['02', '完成重启', 'sudo reboot'], ['03', '重新检查节点', '/dev/spidev1.1']];
    steps.forEach(([n, label, detail], i) => {
      const active = Math.min(2, Math.floor(t / 2.6)) === i;
      s += group(t - i * 1.1, text(940, 107 + i * 157, n, 42, active ? orange : gray) + text(1030, 107 + i * 157, label, 42, active ? orange : ink) + text(1030, 159 + i * 157, detail, 31, gray));
    });
    return s;
  }
  function backlight(t) {
    let s = display(50, 65, 'off', 0, 360, 365);
    s += text(230, 495, '背光不亮', 38, gray, 'middle');
    const rows = [['VCC', '3.3V 供电', '物理 Pin 1 / 17'], ['GND', '共地', '物理 Pin 6'], ['BL', '背光控制', '默认物理 Pin 33']];
    rows.forEach(([name, label, detail], i) => {
      const active = Math.min(2, Math.floor(t / 1.75)) === i;
      const y = 112 + i * 154;
      s += line(410, y, 685, y, active ? orange : '#bbb', active ? 6 : 3);
      s += rect(673, y - 9, 18, 18, active ? orange : '#bbb', 'none', 0);
      s += text(745, y + 12, name, 46, active ? orange : ink);
      s += text(985, y + 12, label, 42) + text(985, y + 61, detail, 30, gray);
    });
    return s;
  }
  function blank(t) {
    let s = display(20, 70, 'blank', 0, 330, 350) + text(185, 486, '背光亮，画面空白', 33, gray, 'middle');
    const names = [['MOSI', '数据', '19'], ['SCLK', '时钟', '23'], ['CS', '片选', '24'], ['DC', '命令 / 数据', '22'], ['RST', '复位', '31']];
    s += text(850, 30, '信号', 29, gray) + text(1080, 30, '作用', 29, gray) + text(1580, 30, '物理管脚', 29, gray, 'end');
    const active = Math.min(4, Math.floor(t / 1.35));
    names.forEach(([name, label, pin], i) => {
      const y = 95 + i * 93, col = i === active ? orange : '#b5b7af';
      s += `<path d="M 350 ${120 + i * 61} H ${485 + i * 35} V ${y - 10} H 785" stroke="${col}" stroke-width="${i === active ? 6 : 3}" fill="none"/>`;
      s += text(850, y, name, 39, i === active ? orange : ink) + text(1080, y, label, 34) + text(1530, y, pin, 37, i === active ? orange : gray, 'middle');
    });
    return s;
  }
  function colors(t) {
    const labels = ['红', '绿', '蓝'], fills = ['#ed3a29', '#24a35b', '#2576dd'];
    const active = Math.min(2, Math.floor(t / 1.1));
    let s = '';
    labels.forEach((label, i) => {
      const x = i * 570;
      s += rect(x, 55, 510, 300, fills[i], i === active ? ink : fills[i], i === active ? 7 : 0);
      s += text(x + 255, 230, label, 76, '#fff', 'middle');
      s += text(x + 255, 412, ['--solid red', '--solid green', '--solid blue'][i], 34, i === active ? ink : gray, 'middle');
      if (i === active) s += line(x, 445, x + 510, 445, orange, 6);
    });
    return s + group(t - 2.4, text(0, 514, '红蓝颠倒时，尝试 --rgb 后重新测试', 35, orange));
  }
  function animation(t) {
    let s = display(0, 65, 'image', 0, 330, 365) + display(520, 65, 'animation', t, 330, 365);
    s += text(165, 490, '静态图正常', 36, ink, 'middle') + text(685, 490, '再检查动画', 36, orange, 'middle');
    s += line(375, 255, 475, 255, orange, 5) + `<path d="M 455 239 L 475 255 L 455 271" fill="none" stroke="${orange}" stroke-width="5"/>`;
    s += text(1000, 109, '动画参数', 43) + text(1000, 168, '颜色、方向、背光设置', 33, gray);
    s += group(t - 1.3, line(1000, 215, 1650, 215, '#bbb', 2) + text(1000, 281, '刷新速度', 43, orange) + text(1000, 348, '--fps 15', 42) + text(1000, 410, '--speed 12000000', 37));
    return s;
  }
  const scenes = [
    ['本课回顾', '从 SPI 原理，到点亮屏幕', '这节课，我们先讲到这里。', '理解通信信号，完成屏幕显示实验。', recap],
    ['排查 01 · 设备节点', '找不到设备节点？', '先确认 SPI 配置，再确认已经重启。', '本课使用 /dev/spidev1.1；节点存在不代表屏幕已接好。', node],
    ['排查 02 · 背光', '背光不亮，先检查这三项', '供电、地和 BL，逐项核对。', '检查或调整接线前，先关机并断开电源。', backlight],
    ['排查 03 · 图像', '背光亮了，为什么没有图像？', '核对数据线、时钟、片选、DC 和复位线。', '背光亮起，只能说明背光已经点亮。', blank],
    ['排查 04 · 颜色', '颜色不对，先做三色测试', '依次显示红、绿、蓝，确认颜色是否对应。', '每次纯色测试结束后，再运行下一条命令。', colors],
    ['排查 05 · 动画', '静态图正常，再检查动画', '确认动画参数，并调整目标帧率与 SPI 时钟。', '--fps 设置目标帧率；实际刷新速度还取决于绘图与传输。', animation]
  ];
  const params = new URLSearchParams(location.search);
  let current = 0, playing = params.get('autoplay') !== '0', last = performance.now();
  if (params.get('export') === '1') document.body.classList.add('export');
  function fit() { $('stage').style.transform = `translate(-50%,-50%) scale(${Math.min(innerWidth / 1920, innerHeight / 1080)})`; }
  function render(value) {
    current = Math.max(0, Math.min(duration, value));
    let i = starts.findIndex((s, j) => j < scenes.length && current >= s && current < starts[j + 1]);
    if (i < 0) i = scenes.length - 1;
    const [kicker, title, sub, note, draw] = scenes[i], local = current - starts[i];
    $('kicker').textContent = kicker; $('title').textContent = title; $('sub').textContent = sub; $('note').textContent = note;
    const a = i === 0 ? 1 : ease(local / .35);
    $('scene').style.opacity = .18 + .82 * a;
    $('scene').style.transform = `translateY(${(1 - a) * 12}px)`;
    $('diagram').innerHTML = draw(local); $('scrub').value = current;
    window.__videoDone = current >= duration;
    return current;
  }
  function seek(t) { last = performance.now(); return render(Number(t) || 0); }
  function button() { $('play').textContent = playing ? '暂停' : '播放'; }
  function pause() { playing = false; button(); }
  function play() { if (current >= duration) seek(0); playing = true; last = performance.now(); button(); }
  function tick(now) { if (playing) { render(current + (now - last) / 1000); if (current >= duration) pause(); } last = now; requestAnimationFrame(tick); }
  window.__spiVideo = { duration, starts: starts.slice(), seek, play, pause, get time() { return current; } };
  $('play').onclick = () => playing ? pause() : play();
  $('restart').onclick = () => { seek(0); play(); };
  $('scrub').oninput = e => { pause(); seek(e.target.value); };
  document.addEventListener('keydown', e => { if (e.key === ' ') { e.preventDefault(); playing ? pause() : play(); } if (e.key === 'ArrowRight') seek(current + 2); if (e.key === 'ArrowLeft') seek(current - 2); if (e.key === 'Home') seek(0); if (e.key === 'End') seek(duration); });
  addEventListener('resize', fit); fit(); seek(params.get('t')); button(); requestAnimationFrame(tick);
})();
