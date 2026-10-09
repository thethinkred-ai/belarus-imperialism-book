# -*- coding: utf-8 -*-
"""Интерактивные дашборды для глав 1–2 (ванильный JS, без внешних зависимостей).
Вставляются в md по плейсхолдеру {{WIDGET:name}} -> <p>{{WIDGET:name}}</p>."""

W_CSS = """
.widget{margin:22px 0;border:1px solid var(--line);border-radius:12px;background:var(--card);padding:16px 18px}
.widget h4{margin:0 0 6px;font-size:16px}
.widget .hint{font-size:13px;color:var(--muted);margin:0 0 12px}
.wrow{display:flex;align-items:center;gap:10px;margin:9px 0;flex-wrap:wrap}
.wrow label{flex:0 0 300px;font-size:14px}
.wrow input[type=range]{flex:1 1 180px;accent-color:#e11d2a}
.wrow output{flex:0 0 92px;font-size:13px;font-variant-numeric:tabular-nums}
.wstatus{display:inline-block;min-width:132px;text-align:center;border-radius:14px;padding:1px 8px;font-size:12px;font-weight:600}
.s-prov{background:#e7f5ee;color:#047857}.s-na{background:#eef0f3;color:#5b636e}.s-ref{background:#fde8e8;color:#c11d2a}
.wverdict{margin-top:12px;background:#fff;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;padding:10px 14px;font-size:14.5px;line-height:1.55}
.wbtns{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.wbtns button{border:1px solid var(--line);background:#fff;border-radius:8px;padding:6px 12px;font-size:13px;cursor:pointer}
.wbtns button:hover{border-color:var(--accent);color:var(--accent)}
.wsel{font-size:13px;padding:4px 6px;border-radius:6px;border:1px solid var(--line);background:#fff}
.wnote{font-size:12.5px;color:var(--muted);margin-top:8px}
@media (max-width:640px){.wrow label{flex:1 1 100%}}
"""

# ---------------------------------------------------------------- W1: конструктор критерия
W1 = """<div class="widget" id="w1">
<h4>Дашборд 1.1. Конструктор критерия К∧В∧Г∧Р и классификации</h4>
<p class="hint">Двигайте ползунки — это «сила свидетельств» по каждому условию критерия (гл. 1 §1.7). Порог отделяет «доказано» от «не установлено»: попробуйте его поднять — и убедитесь, что вывод зависит от стандарта доказательства. Помните правило главы: <b>«не установлено» ≠ «установлено отсутствие»</b>.</p>
<div class="wrow"><label>К — центр командования внутри страны</label><input type="range" id="w1k" min="0" max="100" value="85"><output id="w1ko">85</output><span class="wstatus s-prov" id="w1ks">доказано</span></div>
<div class="wrow"><label>В — внешнее господство (зарубежный контур)</label><input type="range" id="w1v" min="0" max="100" value="30"><output id="w1vo">30</output><span class="wstatus s-na" id="w1vs">не установлено</span></div>
<div class="wrow"><label>Г — государственное закрепление внешнего контура</label><input type="range" id="w1g" min="0" max="100" value="20"><output id="w1go">20</output><span class="wstatus s-na" id="w1gs">не установлено</span></div>
<div class="wrow"><label>Р — воспроизводимость контура</label><input type="range" id="w1r" min="0" max="100" value="35"><output id="w1ro">35</output><span class="wstatus s-na" id="w1rs">не установлено</span></div>
<div class="wrow"><label>Порог «доказано» (стандарт доказательства)</label><input type="range" id="w1thr" min="30" max="95" value="75"><output id="w1thro">75</output><span></span></div>
<div class="wrow"><label>Ось II — структурная зависимость (сила свидетельств)</label><input type="range" id="w1dep" min="0" max="100" value="80"><output id="w1depo">80</output><span class="wstatus s-prov" id="w1deps">доказано</span></div>
<div class="wrow"><label>Внешняя монопольная позиция (тип III, как калий)</label><input type="checkbox" id="w1mono" style="accent-color:#e11d2a"><span class="wnote">отдельный статус — см. гл. 12</span></div>
<div class="wbtns">
<button id="w1p-by">Пресет: Беларусь-2026</button>
<button id="w1p-center">Пресет: империалистический центр</button>
<button id="w1p-sub">Пресет: подчинённый участник</button>
<button id="w1p-none">Пресет: всё не доказано</button>
</div>
<div class="wverdict" id="w1out" aria-live="polite"></div>
<p class="wnote">Схема обучающая: типы I–V и правило «классификация отложена» — гл. 1 §1.6, §1.10; статусы — §1.4.</p>
</div>
<script>
(function(){
 var K=document.getElementById('w1k'),V=document.getElementById('w1v'),G=document.getElementById('w1g'),
     R=document.getElementById('w1r'),T=document.getElementById('w1thr'),D=document.getElementById('w1dep'),
     M=document.getElementById('w1mono');
 function st(v,t){if(v>=t)return['доказано','s-prov'];if(v>=20)return['не установлено','s-na'];return['опровергнуто','s-ref'];}
 function set(id,v){var o=document.getElementById(id+'o');o.textContent=v;}
 function badge(id,txt,cls){var e=document.getElementById(id);e.textContent=txt;e.className='wstatus '+cls;}
 function upd(){
  var t=+T.value;
  [['w1k',K],['w1v',V],['w1g',G],['w1r',R],['w1dep',D]].forEach(function(p){set(p[0],p[1].value);});
  var sk=st(+K.value,t),sv=st(+V.value,t),sg=st(+G.value,t),sr=st(+R.value,t),sd=st(+D.value,t);
  badge('w1ks',sk[0],sk[1]);badge('w1vs',sv[0],sv[1]);badge('w1gs',sg[0],sg[1]);
  badge('w1rs',sr[0],sr[1]);badge('w1deps',sd[0],sd[1]);
  var allProven=sk[0]=='доказано'&&sv[0]=='доказано'&&sg[0]=='доказано'&&sr[0]=='доказано';
  var anyRef=sk[0]=='опровергнуто'||sv[0]=='опровергнуто'||sg[0]=='опровергнуто'||sr[0]=='опровергнуто';
  var subj=allProven?'установлено':'не установлено';
  var html='<b>Собственная субъектность (К∧В∧Г∧Р): '+subj+'.</b> ';
  if(!allProven){
   html+='Конъюнкция не собрана — достаточного основания для положительного вывода нет. ';
   html+='<i>Но «не установлено» ≠ «установлено отсутствие»'+(anyRef?' (а «опровергнуто» хотя бы одного условия всё равно не равняется вечному отрицанию — закрытые зоны могут открыться).':'.')+'</i> ';
  } else {html+='Все четыре условия доказаны — достаточное основание положительного вывода есть. ';}
  var depTxt;
  if(sd[0]=='доказано')depTxt='высокая';
  else if(sd[0]=='опровергнуто')depTxt='низкая';
  else depTxt='не доказана';
  var klass;
  if(allProven&&depTxt=='высокая')klass='Тип II — подчинённый участник с собственными контурами (гипотеза Б)';
  else if(allProven&&depTxt!='высокая')klass='Тип I — империалистический центр';
  else if(!allProven&&depTxt=='высокая')klass=(M.checked?'Тип III — зависимая страна с внешними монопольными позициями':'Тип III/IV — зависимая страна; вопрос о внешней монопольной позиции открыт');
  else klass='Классификация отложена: не доказана ни субъектность, ни структурная зависимость (правило §1.10)';
  html+='<br><b>Рабочая классификация: '+klass+'.</b> ';
  if(!allProven&&depTxt=='высокая'&&!M.checked)html+='(Отметьте «монопольную позицию», чтобы увидеть различение III/IV.) ';
  html+='<br><i>Ось II (структурная зависимость): '+depTxt+'. Бремя доказательства: положительный вывод — на утверждающем, категорическое отрицание — на отрицающем.</i>';
  document.getElementById('w1out').innerHTML=html;
 }
 function preset(k,v,g,r,t,d,m){
  K.value=k;V.value=v;G.value=g;R.value=r;T.value=t;D.value=d;M.checked=m;upd();
 }
 document.getElementById('w1p-by').onclick=function(){preset(85,30,20,35,75,80,false);};
 document.getElementById('w1p-center').onclick=function(){preset(90,85,90,90,75,15,false);};
 document.getElementById('w1p-sub').onclick=function(){preset(85,80,80,85,75,85,true);};
 document.getElementById('w1p-none').onclick=function(){preset(15,15,15,15,75,15,false);};
 [K,V,G,R,T,D].forEach(function(el){el.addEventListener('input',upd);});
 M.addEventListener('change',upd);
 upd();
})();
</script>"""

# ---------------------------------------------------------------- W2: цепочка доказательства
W2 = """<div class="widget" id="w2">
<h4>Дашборд 2.1. Цепочка доказательства: от показателя к классовому результату</h4>
<p class="hint">Задайте статус каждого звена цепочки «показатель → экономическое отношение → механизм присвоения → положение в системе → классовый результат» (гл. 2 §2.2). Видно, почему <b>показатель сам по себе не доказывает категорию</b> и почему пропуск звена делает вывод гипотезой.</p>
<div class="wrow"><label>1. Показатель (статистическая величина)</label>
<select class="wsel" id="w2s1"><option value="prov">доказано</option><option value="na" selected>не установлено</option><option value="ref">опровергнуто</option></select></div>
<div class="wrow"><label>2. Экономическое отношение за показателем</label>
<select class="wsel" id="w2s2"><option value="prov">доказано</option><option value="na" selected>не установлено</option><option value="ref">опровергнуто</option></select></div>
<div class="wrow"><label>3. Механизм присвоения</label>
<select class="wsel" id="w2s3"><option value="prov">доказано</option><option value="na" selected>не установлено</option><option value="ref">опровергнуто</option></select></div>
<div class="wrow"><label>4. Положение субъекта в системе</label>
<select class="wsel" id="w2s4"><option value="prov">доказано</option><option value="na" selected>не установлено</option><option value="ref">опровергнуто</option></select></div>
<div class="wrow"><label>5. Классовый результат</label>
<select class="wsel" id="w2s5"><option value="prov">доказано</option><option value="na" selected>не установлено</option><option value="ref">опровергнуто</option></select></div>
<div class="wbtns">
<button id="w2p-full">Пресет: полная цепочка</button>
<button id="w2p-moroz">Пресет: ловушка «показатель → сразу категория»</button>
<button id="w2p-ref">Пресет: показатель опровергнут</button>
</div>
<div class="wverdict" id="w2out" aria-live="polite"></div>
<p class="wnote">Статусы: «не установлено» — открытый вопрос; «опровергнуто» — цепочка разорвана доказанным отрицанием звена.</p>
</div>
<script>
(function(){
 var ids=['w2s1','w2s2','w2s3','w2s4','w2s5'];
 var names=['показатель','экономическое отношение','механизм присвоения','положение в системе','классовый результат'];
 function upd(){
  var vals=ids.map(function(id){return document.getElementById(id).value;});
  var html='';var i=0;
  while(i<5&&vals[i]=='prov')i++;
  if(i==5){
   html='<b>Вывод установлен по полной цепочке.</b> Показатель доведён до классового результата через отношение, механизм и положение — двойного счёта и подмен нет.';
  } else if(vals[i]=='ref'){
   html='<b>Цепочка разорвана опровержением звена «'+names[i]+'».</b> Это не «недоказанность»: звено опровергнуто, поэтому категория в этой форме к материалу неприменима (статус — опровергнуто, не «отсутствие навсегда»).';
  } else {
   var msgs={
    0:'<b>Основания нет.</b> Пока не установлен даже показатель, категория не применяется вовсе.',
    1:'<b>Ловушка №2 — показатель подменяет категорию.</b> Величина есть, но экономическое отношение за ней не показано: переход к категории запрещён (§2.2).',
    2:'<b>Механизм присвоения не показан.</b> Отношение зафиксировано, но кто, как и через что присваивает — не установлено: вывод остаётся гипотезой, а не результатом.',
    3:'<b>Положение в системе не определено.</b> Механизм есть, но место субъекта в иерархии присвоения не показано — классовый результат преждевременен.',
    4:'<b>Классовый результат — не пятое число.</b> Это теоретический вывод из первых четырёх звеньев; его место — главы 13–14, без них он декларация.'
   };
   html=msgs[i]+' <i>Звеньев доказано: '+i+' из 5.</i>';
  }
  document.getElementById('w2out').innerHTML=html;
 }
 ids.forEach(function(id){document.getElementById(id).addEventListener('change',upd);});
 document.getElementById('w2p-full').onclick=function(){ids.forEach(function(id){document.getElementById(id).value='prov';});upd();};
 document.getElementById('w2p-moroz').onclick=function(){document.getElementById('w2s1').value='prov';ids.slice(1).forEach(function(id){document.getElementById(id).value='na';});upd();};
 document.getElementById('w2p-ref').onclick=function(){document.getElementById('w2s1').value='ref';ids.slice(1).forEach(function(id){document.getElementById(id).value='na';});upd();};
 upd();
})();
</script>"""

# ---------------------------------------------------------------- W3: flow/stock/income
W3 = """<div class="widget" id="w3">
<h4>Дашборд 2.2. Flow / stock / income: почему рост запаса ≠ приток</h4>
<p class="hint">Симулятор международной инвестиционной позиции (метод гл. 2 §2.4, приложение — гл. 9): задайте годовой <b>поток</b> новых инвестиций, реинвестированную прибыль, <b>переоценку</b> (курсы/цены активов) и выплачиваемые <b>доходы</b>. Смотрите: запас растёт — но из чего он состоит? Сам по себе рост позиции не позволяет определить состав прироста.</p>
<div class="wrow"><label>Новый приток (flow), млрд $/год</label><input type="range" id="w3f" min="-2" max="5" step="0.1" value="0.3"><output id="w3fo">0.3</output></div>
<div class="wrow"><label>Реинвестированная прибыль, млрд $/год</label><input type="range" id="w3re" min="0" max="2" step="0.05" value="0.5"><output id="w3reo">0.5</output></div>
<div class="wrow"><label>Переоценка активов, млрд $/год</label><input type="range" id="w3rv" min="-2" max="2" step="0.1" value="0.8"><output id="w3rvo">0.8</output></div>
<div class="wrow"><label>Доходы к выплате (income), млрд $/год</label><input type="range" id="w3in" min="0" max="3" step="0.05" value="1.2"><output id="w3ino">1.2</output></div>
<div class="wrow"><label>Начальный запас (stock), млрд $</label><input type="range" id="w3s0" min="0" max="5" step="0.1" value="1.5"><output id="w3s0o">1.5</output></div>
<div class="wverdict" id="w3table" aria-live="polite"></div>
<p class="wnote">Упрощение: запас(t+1) = запас(t) + приток + реинвест + переоценка. Доходы (income) в запас не входят — они пересекают границу как платежи. Реальный кейс — гл. 9 §9.4: запас прямых инвестиций РБ за рубежом вырос с 1.34 до 2.66 млрд $ (2022→2026), и декомпозиция этого роста неизвестна.</p>
</div>
<script>
(function(){
 var F=document.getElementById('w3f'),RE=document.getElementById('w3re'),RV=document.getElementById('w3rv'),
     IN=document.getElementById('w3in'),S0=document.getElementById('w3s0');
 function num(id){return +document.getElementById(id).textContent;}
 function upd(){
  [['w3f',F],['w3re',RE],['w3rv',RV],['w3in',IN],['w3s0',S0]].forEach(function(p){
   document.getElementById(p[0]+'o').textContent=(+p[1].value).toFixed(2).replace('.',',');});
  var f=+F.value,re=+RE.value,rv=+RV.value,inc=+IN.value,s=+S0.value;
  var s0=s;
  var rows='<tr><th>Год</th><th>Запас на 1.01</th><th>Приток</th><th>Реинвест</th><th>Переоценка</th><th>Доходы к выплате</th><th>Запас на 31.12</th></tr>';
  var totFlow=0,totRev=0;
  for(var y=1;y<=5;y++){
   var end=s+f+re+rv;
   rows+='<tr><td>'+y+'</td><td>'+s.toFixed(2)+'</td><td>'+f.toFixed(2)+'</td><td>'+re.toFixed(2)+'</td><td>'+rv.toFixed(2)+'</td><td>'+inc.toFixed(2)+'</td><td><b>'+end.toFixed(2)+'</b></td></tr>';
   totFlow+=f;totRev+=rv;s=end;
  }
  var growth=s-s0;
  var shareReval=(growth!=0)?(totRev/growth*100):0;
  var verdict;
  if(growth<=0){verdict='Запас <b>не растёт</b>: приток не покрывает отрицательную переоценку/отток. Отсутствие роста запаса — тоже не «отсутствие потоков».';}
  else if(shareReval>50){verdict='<b>Более половины прироста запаса — переоценка</b> ('+Math.round(shareReval)+'%). Сам по себе рост позиции <b>не доказывает новые инвестиции</b>: нужна декомпозиция (гл. 9 §9.4).';}
  else {verdict='Переоценка объясняет только '+Math.round(shareReval)+'% прироста: рост запаса в основном из потоков (приток + реинвест). Но и это <b>не отвечает на вопрос о механизме присвоения</b> — нужны доходы (income) и реинвестиции по компонентам.';}
  document.getElementById('w3table').innerHTML=
   '<table style="margin:8px 0;font-size:13px">'+rows+'</table><b>Прирост запаса за 5 лет: '+growth.toFixed(2)+' млрд $.</b> '+verdict+
   '<br><i>Доходы к выплате за 5 лет: '+(inc*5).toFixed(2)+' млрд $ — это income, они меняют платёжный баланс, но не запас.</i>';
 }
 [F,RE,RV,IN,S0].forEach(function(el){el.addEventListener('input',upd);});
 upd();
})();
</script>"""

ALL = {
    'classifier': ('Дашборд 1.1. Критерий К∧В∧Г∧Р и типология', W1),
    'chain': ('Дашборд 2.1. Цепочка доказательства', W2),
    'flowstock': ('Дашборд 2.2. Flow / stock / income', W3),
}
