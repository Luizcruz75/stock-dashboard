// dashboard.js — lógica auxiliar do dashboard de ações

// Aplica Plotly.relayout com responsive: true após redimensionamento da janela
window.addEventListener('resize', () => {
  document.querySelectorAll('.js-plotly-plot').forEach(div => {
    Plotly.relayout(div, { autosize: true });
  });
});
