// Automatically display the current year in the footer.
const currentYear = document.getElementById("currentYear");

if (currentYear) {
    currentYear.textContent = new Date().getFullYear();
}

// Temporary behaviour for the static support form.
// Django will later save this information in the database.
const supportApplication = document.getElementById(
    "supportApplication"
);

if (supportApplication) {
    supportApplication.addEventListener("submit", function (event) {
        event.preventDefault();

        alert(
            "Your support application has been captured for this demonstration. Database submission will be connected through Django."
        );

        supportApplication.reset();
    });
}

// Temporary behaviour for the static volunteer form.
const volunteerApplication = document.getElementById(
    "volunteerApplication"
);

if (volunteerApplication) {
    volunteerApplication.addEventListener("submit", function (event) {
        event.preventDefault();

        alert(
            "Your volunteer application has been captured for this demonstration. Database submission will be connected through Django."
        );

        volunteerApplication.reset();
    });
}

// Temporary contact form behaviour.
// Django will later save enquiries in the database.
const contactForm = document.getElementById("contactForm");

if (contactForm) {
    contactForm.addEventListener("submit", function (event) {
        event.preventDefault();

        alert(
            "Thank you. Your message has been captured for this demonstration. Database submission will be connected through Django."
        );

        contactForm.reset();
    });
}