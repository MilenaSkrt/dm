// ---------------- АНИМАЦИЯ ДВИЖЕНИЯ ----------------
function startAnimation() {
    const canvas = document.getElementById("canvas");

    if (!canvas) return; // если нет canvas — просто не запускаем

    const ctx = canvas.getContext("2d");

    let x = 0;

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // движение тела по синусоиде (как механика)
        let y = canvas.height / 2 + 50 * Math.sin(x * 0.05);

        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);
        ctx.fillStyle = "#002FE7";
        ctx.fill();

        x += 2;
        if (x > canvas.width) x = 0;

        requestAnimationFrame(draw);
    }

    draw();
}


// ---------------- API ЗАПРОСЫ ----------------

// универсальный fetch
async function apiRequest(url, method = "GET", data = null) {
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
        console.error("Ошибка API:", response.status);
        return null;
    }

    return await response.json();
}


// ---------------- ЛОГИН ----------------

async function loginUser(event) {
    event.preventDefault();

    const form = event.target;

    const formData = new FormData(form);

    const response = await fetch("/login", {
        method: "POST",
        body: new URLSearchParams(formData)
    });

    if (!response.ok) {
        alert("Ошибка входа");
        return;
    }

    const data = await response.json();

    // сохраняем токен
    localStorage.setItem("token", data.access_token);

    alert("Успешный вход!");
    window.location.href = "/";
}


// ---------------- ЗАГРУЗКА ДАННЫХ ----------------

async function loadModules() {
    const modules = await apiRequest("/modules/");
    console.log("Modules:", modules);
}

async function loadTasks() {
    const tasks = await apiRequest("/tasks/");
    console.log("Tasks:", tasks);
}


// ---------------- INIT ----------------

document.addEventListener("DOMContentLoaded", () => {
    startAnimation();
});