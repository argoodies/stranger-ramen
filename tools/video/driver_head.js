<script>
// video capture: the page runs on a virtual clock that only moves when the recorder says so
window.__VT = 0; performance.now = () => window.__VT; window.requestAnimationFrame = () => 0;
</script>
