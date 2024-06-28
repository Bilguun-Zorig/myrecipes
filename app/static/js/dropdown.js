document.addEventListener('DOMContentLoaded', function () {
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const hiddenInput = document.getElementById('category');

    dropdownItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const value = this.getAttribute('data-value');
            const text = this.textContent;

            dropdownToggle.textContent = text;
            hiddenInput.value = value;
        });
    });
});


    document.querySelectorAll('.heart-checkbox').forEach(item => {
        item.addEventListener('click', event => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;
            event.preventDefault();
        });
    });
