const colors = { accent2: '#968AE1', accent3: '#FFF854', accent4: '#002FE7', accent5: '#FF7641', accent1: '#81818B', card_bg: '#F5F5F7' };

function initProjectileAnimation() {
    const canvas = document.getElementById('projectileAnimCanvas');
    if (!canvas) return;
    canvas.width = canvas.clientWidth; canvas.height = 220;
    let time = 0;
    function calc(v0=28, a=50, h0=0) { const g=9.81, r=a*Math.PI/180, vx=v0*Math.cos(r), vy=v0*Math.sin(r), tf=(vy+Math.sqrt(vy*vy+2*g*h0))/g; return {vx,vy,tf}; }
    function draw() {
        const ctx = canvas.getContext('2d'), w = canvas.width, h = canvas.height;
        const {vx,vy,tf} = calc(); const g=9.81;
        ctx.clearRect(0,0,w,h);
        ctx.fillStyle = colors.accent1+'40'; ctx.fillRect(0,h-30,w,30);
        let t = time; if(t>tf) t=tf;
        const x=vx*t, y=vy*t-0.5*g*t*t, maxX=vx*tf, maxY=vy*vy/(2*g);
        if(maxX>0 && maxY>0) {
            const x_px = (x/maxX)*(w-50)+25, y_px = h-35 - (y/maxY)*(h-65);
            ctx.beginPath(); ctx.arc(x_px,y_px,8,0,Math.PI*2); ctx.fillStyle=colors.accent5; ctx.fill();
            ctx.beginPath(); ctx.arc(x_px,y_px,3,0,Math.PI*2); ctx.fillStyle='white'; ctx.fill();
        }
        time += 0.035; if(time>tf) time=0;
        requestAnimationFrame(draw);
    }
    draw();
}

function initSpringAnimation() {
    const canvas = document.getElementById('springAnimCanvas');
    if (!canvas) return;
    canvas.width = canvas.clientWidth; canvas.height = 220;
    let time = 0;
    function getDisp(t) { const omega0=Math.sqrt(45/0.8), zeta=2.5/(2*Math.sqrt(0.8*45)), x0=35; if(zeta<1){ const w=omega0*Math.sqrt(1-zeta*zeta); return x0*Math.exp(-zeta*omega0*t)*Math.cos(w*t); } return x0*Math.exp(-zeta*omega0*t)*(1+zeta*omega0*t); }
    function draw() {
        const ctx = canvas.getContext('2d'), w = canvas.width, h = canvas.height;
        ctx.clearRect(0,0,w,h);
        ctx.fillStyle=colors.accent1; ctx.fillRect(0,0,w,15);
        const cx=w/2, disp=getDisp(time), cy=150+disp;
        ctx.beginPath();
        for(let i=0;i<=18;i++){ const t=i/18, y=20+(cy-12-20)*t, amp=12*(1+Math.abs(disp)/80), xo=Math.sin(t*Math.PI*6)*amp; if(i===0) ctx.moveTo(cx+xo,y); else ctx.lineTo(cx+xo,y); }
        ctx.strokeStyle=colors.accent4; ctx.lineWidth=2.5; ctx.stroke();
        ctx.fillStyle=colors.accent5; ctx.fillRect(cx-22,cy-14,44,28);
        ctx.fillStyle=colors.accent3; ctx.fillRect(cx-14,cy-9,28,18);
        time+=0.04; if(time>5) time=0;
        requestAnimationFrame(draw);
    }
    draw();
}

function initCannonAnimation() {
    const canvas = document.getElementById('cannonAnimCanvas');
    if (!canvas) return;
    canvas.width = canvas.clientWidth; canvas.height = 220;
    let time = 0;
    function calc(v0=38, a=45, h0=20) { const g=9.81, r=a*Math.PI/180, vx=v0*Math.cos(r), vy=v0*Math.sin(r), tf=(vy+Math.sqrt(vy*vy+2*g*h0))/g; return {vx,vy,tf}; }
    function draw() {
        const ctx = canvas.getContext('2d'), w = canvas.width, h = canvas.height;
        const {vx,vy,tf}=calc(); const g=9.81;
        ctx.clearRect(0,0,w,h);
        ctx.fillStyle=colors.accent1+'40'; ctx.fillRect(0,h-28,w,28);
        const cx=35, cy=h-40, rad=45*Math.PI/180;
        ctx.save(); ctx.translate(cx,cy); ctx.rotate(-rad); ctx.fillStyle=colors.accent4; ctx.fillRect(0,-7,38,14); ctx.restore();
        ctx.beginPath(); ctx.arc(cx-6,cy+6,8,0,Math.PI*2); ctx.fillStyle=colors.accent1; ctx.fill();
        ctx.beginPath(); ctx.arc(cx+24,cy+6,8,0,Math.PI*2); ctx.fillStyle=colors.accent1; ctx.fill();
        let t=time; if(t>tf) t=tf;
        const x=vx*t, y=20+vy*t-0.5*g*t*t, maxX=vx*tf, maxY=vy*vy/(2*g)+20;
        if(maxX>0 && t<tf) {
            const x_px = cx+45+(x/maxX)*(w-cx-70), y_px = h-38-(y/maxY)*(h-70);
            ctx.beginPath(); ctx.arc(x_px,y_px,7,0,Math.PI*2); ctx.fillStyle=colors.accent5; ctx.fill();
        }
        time+=0.04; if(time>tf) time=0;
        requestAnimationFrame(draw);
    }
    draw();
}

document.addEventListener('DOMContentLoaded', () => {
    initProjectileAnimation();
    initSpringAnimation();
    initCannonAnimation();
});