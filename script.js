// --- CRISPR Simulation Logic ---
document.getElementById('crisprForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const original = document.getElementById('original').value.trim().toUpperCase();
  const target = document.getElementById('target').value.trim().toUpperCase();
  const replacement = document.getElementById('replacement').value.trim().toUpperCase();
  const resultBox = document.getElementById('resultText');

  if (!original.includes(target)) {
    resultBox.innerHTML = `❌ Target sequence not found in the original DNA.`;
    return;
  }

  // Replace first occurrence
  const editedDNA = original.replace(target, replacement);

  // Highlight edited section
  const highlighted = original.replace(target, `<span style="color:#ff4f4f;">${target}</span>`);
  const newHighlighted = editedDNA.replace(replacement, `<span style="color:#00ffc6;">${replacement}</span>`);

  resultBox.innerHTML = `
    <strong>Before Edit:</strong> ${highlighted}<br><br>
    <strong>After CRISPR Edit:</strong> ${newHighlighted}<br><br>
    <strong>Explanation:</strong> The CRISPR complex located the target sequence <span style="color:#ff4f4f;">${target}</span> 
    and replaced it with <span style="color:#00ffc6;">${replacement}</span> successfully.
  `;

  animateDNAEdit();
});

// --- DNA Animation ---
const canvas = document.getElementById('dnaCanvas');
const ctx = canvas.getContext('2d');
let t = 0;

function drawDNA() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const centerY = canvas.height / 2;
  const amplitude = 60;
  const wavelength = 30;
  const speed = 0.08;

  for (let x = 0; x < canvas.width; x += 10) {
    const y1 = centerY + Math.sin((x / wavelength) + t) * amplitude;
    const y2 = centerY + Math.sin((x / wavelength) + t + Math.PI) * amplitude;

    ctx.beginPath();
    ctx.moveTo(x, y1);
    ctx.lineTo(x, y2);
    ctx.strokeStyle = 'rgba(0,255,198,0.4)';
    ctx.stroke();

    // Dots for backbone
    ctx.beginPath();
    ctx.arc(x, y1, 3, 0, Math.PI * 2);
    ctx.arc(x, y2, 3, 0, Math.PI * 2);
    ctx.fillStyle = '#00ffc6';
    ctx.fill();
  }

  t += speed;
  requestAnimationFrame(drawDNA);
}
drawDNA();

function animateDNAEdit() {
  let flash = 0;
  const flashInterval = setInterval(() => {
    canvas.style.boxShadow = (flash % 2 === 0)
      ? "0 0 30px #ff4f4f"
      : "0 0 30px #00ffc6";
    flash++;
    if (flash > 6) {
      clearInterval(flashInterval);
      canvas.style.boxShadow = "0 0 25px rgba(0, 255, 198, 0.1)";
    }
  }, 200);
}
