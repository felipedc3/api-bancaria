

const API_URL = "http://127.0.0.1:8000";

let loadingStatement = false;

/**
 * Retorna o token JWT salvo no localStorage.
 * Se não houver token, redireciona para o login,
 * impedindo acesso ao dashboard sem autenticação.
 */
function getToken() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/";
        return null;
    }
    return token;
}

/**
 * Formata um valor numérico para o padrão monetário brasileiro.
 * Exemplo: 1000.5 → "R$ 1.000,50"
 */
function formatCurrency(value) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL"
    }).format(value)
}

/**
 * Formata uma data ISO para o padrão brasileiro.
 * Exemplo: "2026-04-10T17:18:29" → "10/04/2026 17:18"
 */
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}

/**
 * Realiza o logout do usuário.
 * Remove o token do localStorage e redireciona para o login.
 */
function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

/**
 * Busca os dados da conta do usuário autenticado na API
 * e atualiza o saldo e número da conta na tela.
 */
async function loadAccount() {
    const token = getToken();
    if (!token) return;

    try {
        const response = await fetch(`${API_URL}/accounts/me`, {
            headers: {"Authorization": `Bearer ${token}`}
        });

        if (response.status === 401 || response.status === 403) {
            logout();
            return;
        }

        const account = await response.json();

        //Atualiza o saldo e o número da conta na tela.
        document.getElementById("balance").textContent = formatCurrency(account.balance);
        document.getElementById("account-id").textContent = account.id;

    } catch (error) {
        console.error("Erro ao carregar a conta", error);
    }
    
}

/**
 * Busca o extrato da conta na API e renderiza
 * cada transação como um item da lista.
 */
async function loadStatement() {
    if (loadingStatement) return;
    loadingStatement = true;

    const token = getToken();
    if (!token) {
        loadingStatement = false
        return;
    }

    try {
        const response = await fetch(`${API_URL}/transactions/statement`, {
            headers: {"Authorization": `Bearer ${token}` }
        });

        if (response.status === 401 || response.status === 403) {
            loadingStatement = false;
            logout();
            return;
        }

        const transactions = await response.json();
        const list = document.getElementById("statement-list");

        if (!Array.isArray(transactions)) {
            console.error("Resposta inválida:", transactions);
            loadingStatement = false;
            return;
        }

        //Se não houver transa~]oes, exibe uma mensagem informativa.
        if (transactions.length === 0) {
            list.innerHTML = `<li class="empty-statement">Nenhuma transação encontrada`;
            loadingStatement = false;
            return;
        }

        // Ícones e labels para cada tipo de transação.
        const icons = {
            deposito: "",
            saque: "",
            transferencia: ""
        };

        const labels = {
            deposito: "Depósito",
            saque: "Saque",
            transferencia: "Transferência"
        };

        // Renderiza cada transação como um item da lista.
        list.innerHTML = transactions.map(t => `
            <li class="statement-item">
                <div class="transaction-info">
                    <div class="transaction-icon icon-${t.type}">
                        ${icons[t.type]}
                    </div>
                    <div class="transaction-details">
                        <strong>${labels[t.type]}</strong>
                        <span>${formatDate(t.created_at)}</span>
                    </div>
                </div>
                <div class="transaction-amount amount-${t.type}">
                    ${t.type === "deposito" ? "+" : "-"}${formatCurrency(t.amount)}
                </div>
            </li>
        `).join("");

    } catch (error) {
        console.error("Erro ao carregar extrato:", error);
    }

    loadingStatement = false
}

/**
 * Realiza um depósito na conta do usuário.
 * Após o depósito, atualiza o saldo e o extrato na tela.
 */
async function deposit() {
    const token = getToken();
    const amount = parseFloat(document.getElementById("deposit-amount").value);

    if (!amount || amount <= 0) {
        alert("Digite um valor válido para o depósito.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/transactions/deposit`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ amount })
        });

        if (response.ok) {
            document.getElementById("deposit-amount").value = "";
            // Atualiza o saldo e extrato após o depósito.
            await loadAccount();
            await loadStatement();
        } 
        
        if (response.status === 401) {
            logout();
            return;
        } else {
            const data = await response.json();
            alert(data.detail);
        }

    } catch (error) {
        console.error("Erro ao realizar depósito:", error);
    }
}

/**
 * Realiza um saque na conta do usuário.
 * Após o saque, atualiza o saldo e o extrato na tela.
 */
async function withdraw() {
    const token = getToken();
    const amount = parseFloat(document.getElementById("withdraw-amount").value);

    if (!amount || amount <= 0) {
        alert("Digite um valor válido para o saque.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/transactions/withdraw`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ amount })
        });

        if (response.ok) {
            document.getElementById("withdraw-amount").value = "";
            await loadAccount();
            await loadStatement();
        } else {
            const data = await response.json();
            alert(data.detail);
        }

    } catch (error) {
        console.error("Erro ao realizar saque:", error);
    }
}

/**
 * Realiza uma transferência para outra conta.
 * Após a transferência, atualiza o saldo e o extrato na tela.
 */
async function transfer() {
    const token = getToken();
    const targetAccountId = parseInt(document.getElementById("transfer-account").value);
    const amount = parseFloat(document.getElementById("transfer-amount").value);

    if (!targetAccountId || targetAccountId <= 0) {
        alert("Digite um número de conta válido.");
        return;
    }

    if (!amount || amount <= 0) {
        alert("Digite um valor válido para a transferência.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/transactions/transfer`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                target_account_id: targetAccountId,
                amount
            })
        });

        if (response.ok) {
            document.getElementById("transfer-account").value = "";
            document.getElementById("transfer-amount").value = "";
            await loadAccount();
            await loadStatement();
        } else {
            const data = await response.json();
            alert(data.detail);
        }

    } catch (error) {
        console.error("Erro ao realizar transferência:", error);
    }
}

// Carrega os dados da conta e extrato assim que a página abre.
window.onload = () => {
    loadAccount();
    loadStatement();
};

