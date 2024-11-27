const App = () => {
    const [token, setToken] = React.useState(null);
    const [isRedirecting, setIsRedirecting] = React.useState(false);
    const [redirectionTimer, setRedirectionTimer] = React.useState(3); // 3 seconds

    // Получение токена из URL и сохранение в localStorage
    React.useEffect(() => {
        const queryParams = new URLSearchParams(window.location.search);
        const tokenFromUrl = queryParams.get("token");
        console.log(tokenFromUrl)

        // Если токен найден в URL
        if (tokenFromUrl) {
            localStorage.setItem("authToken", tokenFromUrl); // Сохраняем токен в localStorage
            setToken(tokenFromUrl); // Сохраняем токен в состояние для отображения

            // Перенаправление на главную страницу через 3 секунды
            setIsRedirecting(true);
            const interval = setInterval(() => {
                setRedirectionTimer((prevTimer) => prevTimer - 1);
            }, 1000);

            // Очистка интервала при перенаправлении
            setTimeout(() => {
                clearInterval(interval);
                window.location.href = "https://563d76a7-6ee1-415d-82b9-8c923d32acb9.tunnel4.com/index.html"; // Укажите ваш URL
            }, 3000);
        } else {
            // Если токен не найден в URL, то извлекаем его из localStorage
            const storedToken = localStorage.getItem("authToken");
            console.log(storedToken)
            if (storedToken) {
                setToken(storedToken); // Сохраняем токен из localStorage в состояние
            }
        }
    }, []);

    return (
        <div>
            <strong>Веб-приложение</strong>
            <p>Ваш токен:</p>
            <p style={{ fontWeight: "bold", color: "blue" }}>{token || "Токен не найден"}</p>
            {isRedirecting && (
                <p>Перенаправление на главную страницу через {redirectionTimer} секунды...</p>
            )}
        </div>
    );
};

ReactDOM.render(<App />, document.getElementById("root"));
