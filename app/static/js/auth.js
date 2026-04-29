// URL base da API. Como o frontend é servido pelo mesmo servidor,
// podemos usar uma URL relativa sem precisar do endereço completo.

const API_URL = "http://127.0.0.1:8000";

/**
 * Alterna entre as abas de Login e Cadastro.
 * Esconde o formulário atual e exibe o selecionado, além de atualizar o estilo da aba ativa.
 */

function showTab(tab) {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form")
    const tabs = document.querySelectorAll(".auth-tab")

    tabs.forEach(t => t.classList.remove("active"));

    if (tab == "login") {
        loginForm.style.display = "block";
        registerForm.style.display = "none";
        tabs[0].classList.add("active");
    } else {
        loginForm.style.display = "none";
        registerForm.style.display = "block";
        tabs[1].classList.add("active");
    }

    hideAlert();
}

/**
 * Exibe uma mensagem de alerta na tela.
 * O tipo define a cor: "error" para vermelho, "success" para verde.
 */

function showAlert(message, type) {
    const alert = document.getElementById("alert");
    alert.textContent = message;
    alert.className = `alert alert-${type}`;
    alert.style.display = "block";
}

/**
 * Esconde o alerta atual.
 */
function hideAlert() {
    const alert = document.getElementById("alert");
    alert.style.display = "none";
}

/**
 * Realiza o login do usuário.
 * Envia as credenciais para a API e salva o token JWT
 * no localStorage para uso nas próximas requisições.
 */
async function login() {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    if (!email || !password) {
        showAlert("Preencha todos os campos.", "error");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json"},
            body: JSON.stringify({ email, password})
        });

        const data = await response.json();

        if (!response.ok) {
            showAlert(data.detail, "error");
            return;
        }

        // Salva o token no localStorage para usar nas próximas requisições.
        // O localStorage persiste os dados mesmo após fechar o navegador,
        // mantendo o usuário logado até ele clicar em sair.
        localStorage.setItem("token", data.access_token);

        // Redireciona para o dashboard após login bem sucedido.
        window.location.href = "/static/dashboard.html";

    } catch (error) {
        showAlert("Erro ao conectar com o servidor.", "error");
    }
}

/**
 * Realiza o cadastro de um novo usuário.
 * Após o cadastro bem sucedido, faz login automaticamente
 * para não precisar digitar as credenciais novamente.
 */
async function register() {
    const name = document.getElementById("register-name").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    if (!name || !email || !password) {
        showAlert("Preencha todos os campos.", "error");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showAlert(data.detail, "error");
            return;
        }

        // Após cadastro bem sucedido, preenche o formulário de login
        // e faz o login automaticamente para melhor experiência do usuário.
        showAlert("Conta criada com sucesso! Fazendo login...", "success");
        document.getElementById("login-email").value = email;
        document.getElementById("login-password").value = password;

        setTimeout(async () => {
            showTab("login");
            await login();
        }, 1500);

    } catch (error) {
        showAlert("Erro ao conectar com o servidor.", "error");
    }
}