document.addEventListener("DOMContentLoaded", () => {
    const emailInput = document.getElementById("email");
    const firstNameInput = document.getElementById("firstName");
    const lastNameInput = document.getElementById("lastName");
    const roomInput = document.getElementById("room");
    const errorDiv = document.getElementById("error");
    const successDiv = document.getElementById("success");
    const form = document.getElementById("registrationForm");

    const regex = /^([a-zA-Z_-]+)\.([a-zA-Z0-9_-]+)@(centrale|enscl|iteem|ig2i)\.centralelille\.fr$/;

    function validateEmail(email) {
        return regex.test(email);
    }

    function extractNames(email) {
        const match = email.match(regex);
        if (match) {
            return {
                firstName: capitalize(match[1]),
                lastName: capitalize(match[2])
            };
        }
        return null;
    }

    function capitalize(str) {
        if (!str) return "";
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    function normalizeRoom(value) {
        return value ? value.toUpperCase() : "";
    }

    emailInput.addEventListener("input", () => {
        if (!validateEmail(emailInput.value)) {
            emailInput.style.borderColor = "red";
        } else {
            emailInput.style.borderColor = "green";

            const names = extractNames(emailInput.value);
            if (names) {
                if (firstNameInput.value === "") firstNameInput.value = names.firstName;
                if (lastNameInput.value === "") lastNameInput.value = names.lastName;
            }
        }
    });

    roomInput.addEventListener("input", () => {
        roomInput.value = normalizeRoom(roomInput.value);
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorDiv.textContent = "";
        successDiv.textContent = "";

        const payload = {
            email: emailInput.value,
            first_name: firstNameInput.value,
            last_name: lastNameInput.value,
            room: roomInput.value || null,
        };

        const resp = await fetch("/register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload),
        });

        if (resp.ok) {
            const data = await resp.json();
            successDiv.textContent = "Utilisateur " + data.username + " créé avec succès ! Vous avez reçu un email pour activer votre compte.";
        } else {
            const err = await resp.json();
            errorDiv.textContent = err.detail || "Erreur serveur";
        }
    });
});
