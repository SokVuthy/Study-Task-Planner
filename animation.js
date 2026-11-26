(function () {
    "use strict";

    //========== SETTINGS==========

    var SWIPE_THRESHOLD = 110;
    var TRASH_SVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>';

    // =============SUMMARY PAGE: COUNT-UP NUMBERS==============
    
    function animateCounters() {
        document.querySelectorAll('.count-up:not([data-done])').forEach(function (el) {
            el.dataset.done = '1';

            var target = parseInt(el.textContent, 10) || 0;
            var start = performance.now();
            var duration = 900;
            el.textContent = '0';

            function step(now) {
                var progress = Math.min((now - start) / duration, 1);
                var eased = 1 - Math.pow(1 - progress, 3);
                el.textContent = Math.round(target * eased);
                if (progress < 1) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        });
    }


    // =================SUMMARY PAGE: PROGRESS BAR===============

    function animateProgress() {
        document.querySelectorAll('.progress-fill:not([data-done])').forEach(function (el) {
            el.dataset.done = '1';

            var width = el.style.width;
            el.style.width = '0%';
            setTimeout(function () { el.style.width = width; }, 80);
        });
    }


    // =================VIEW TASKS PAGE: SWIPE LEFT TO DELETE===========

    function findTrashButton(card) {
        var row = card.closest('[data-testid="stHorizontalBlock"]');
        return row ? row.querySelector('[class*="st-key-trash_"] button') : null;
    }

    function bindSwipe(card) {
        if (card.dataset.swipeBound) return;
        card.dataset.swipeBound = '1';

        var host = card.parentElement;
        var startX = 0;
        var startY = 0;
        var dx = 0;
        var pointerId = null;
        var active = false;
        var dragging = false;
        var armed = false;
        var background = null;

        function resetStyles(delay) {
            setTimeout(function () {
                card.style.translate = '';
                card.style.opacity = '';
                card.style.transition = '';
                card.classList.remove('dragging');
                if (background && background.parentNode) {
                    background.parentNode.removeChild(background);
                }
                background = null;
                host.style.clipPath = '';
                host.style.position = '';
            }, delay);
        }

        card.addEventListener('pointerdown', function (e) {
            if (e.pointerType === 'mouse' && e.button !== 0) return;
            if (!findTrashButton(card)) return;

            active = true;
            dragging = false;
            armed = false;
            dx = 0;
            startX = e.clientX;
            startY = e.clientY;
            pointerId = e.pointerId;
        });

        card.addEventListener('pointermove', function (e) {
            if (!active) return;

            var moveX = e.clientX - startX;
            var moveY = e.clientY - startY;

            if (!dragging) {
                if (Math.abs(moveY) > 12 && Math.abs(moveY) > Math.abs(moveX)) {
                    active = false;
                    return;
                }
                if (Math.abs(moveX) < 8) return;

                dragging = true;
                try { card.setPointerCapture(pointerId); } catch (err) {}

                host.style.position = 'relative';
                host.style.clipPath = 'inset(-24px 0 -24px 0)';

                background = document.createElement('div');
                background.className = 'swipe-bg';
                background.style.height = card.offsetHeight + 'px';
                background.innerHTML = TRASH_SVG + '<span class="swipe-text">Swipe to delete</span>';
                host.insertBefore(background, card);

                card.classList.add('dragging');
                card.style.transition = 'none';
            }

            dx = Math.min(0, moveX);
            card.style.translate = dx + 'px 0';
            background.style.opacity = String(0.35 + Math.min(1, -dx / SWIPE_THRESHOLD) * 0.65);

            var nowArmed = -dx >= SWIPE_THRESHOLD;
            if (nowArmed !== armed) {
                armed = nowArmed;
                background.classList.toggle('armed', armed);
                background.querySelector('.swipe-text').textContent =
                    armed ? 'Release to delete' : 'Swipe to delete';
            }
        });

        function finishSwipe() {
            if (!active) return;
            active = false;
            if (!dragging) return;
            dragging = false;
            try { card.releasePointerCapture(pointerId); } catch (err) {}

            if (-dx >= SWIPE_THRESHOLD) {
                card.style.transition = 'translate 0.28s ease, opacity 0.28s ease';
                card.style.translate = '-110% 0';
                card.style.opacity = '0';

                setTimeout(function () {
                    var button = findTrashButton(card);
                    if (button) button.click();
                }, 260);

                setTimeout(function () {
                    card.style.transition = 'translate 0.35s ease, opacity 0.35s ease';
                    card.style.translate = '0px 0';
                    card.style.opacity = '1';
                    if (background) background.style.opacity = '0';
                }, 450);

                resetStyles(850);
            } else {
                card.style.transition = 'translate 0.3s cubic-bezier(0.22, 1, 0.36, 1)';
                card.style.translate = '0px 0';
                if (background) background.style.opacity = '0';
                resetStyles(320);
            }
            armed = false;
        }

        card.addEventListener('pointerup', finishSwipe);
        card.addEventListener('pointercancel', finishSwipe);
    }

    // ================= WATCH THE PAGE (Streamlit redraws it after every action)==================

    function scan() {
        animateCounters();
        animateProgress();
        document.querySelectorAll('.task-card').forEach(function (card) {
            bindSwipe(card);
        });
    }

    var queued = false;
    new MutationObserver(function () {
        if (queued) return;
        queued = true;
        requestAnimationFrame(function () {
            queued = false;
            scan();
        });
    }).observe(document.body, { childList: true, subtree: true });

    scan();
})();