// Canvas-Based Certificate Generator

function generateCertificate(candidateName, quizTitle, scorePercentage, dateStr) {
  const canvas = document.createElement("canvas");
  canvas.width = 1200;
  canvas.height = 800;
  const ctx = canvas.getContext("2d");

  // Background
  const gradient = ctx.createLinearGradient(0, 0, 1200, 800);
  gradient.addColorStop(0, "#0a0e17");
  gradient.addColorStop(0.5, "#111827");
  gradient.addColorStop(1, "#0a0e17");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 1200, 800);

  // Outer Golden / Cyan Border
  ctx.strokeStyle = "#06b6d4";
  ctx.lineWidth = 6;
  ctx.strokeRect(30, 30, 1140, 740);

  // Inner Thin Accent Border
  ctx.strokeStyle = "rgba(99, 102, 241, 0.4)";
  ctx.lineWidth = 2;
  ctx.strokeRect(45, 45, 1110, 710);

  // Decorative Corner Accents
  const drawCorner = (x, y) => {
    ctx.strokeStyle = "#a855f7";
    ctx.lineWidth = 4;
    ctx.strokeRect(x, y, 40, 40);
  };
  drawCorner(50, 50);
  drawCorner(1110, 50);
  drawCorner(50, 710);
  drawCorner(1110, 710);

  // Title
  ctx.textAlign = "center";
  ctx.fillStyle = "#9ca3af";
  ctx.font = "bold 20px 'Outfit', sans-serif";
  ctx.letterSpacing = "6px";
  ctx.fillText("ONLINE QUIZ SYSTEM & CERTIFICATION", 600, 140);

  ctx.fillStyle = "#ffffff";
  ctx.font = "800 48px 'Outfit', sans-serif";
  ctx.fillText("CERTIFICATE OF ACHIEVEMENT", 600, 210);

  ctx.fillStyle = "#9ca3af";
  ctx.font = "20px 'Inter', sans-serif";
  ctx.fillText("This is officially awarded to", 600, 280);

  // Candidate Name
  const nameGrad = ctx.createLinearGradient(300, 340, 900, 340);
  nameGrad.addColorStop(0, "#06b6d4");
  nameGrad.addColorStop(0.5, "#818cf8");
  nameGrad.addColorStop(1, "#c084fc");
  ctx.fillStyle = nameGrad;
  ctx.font = "bold 56px 'Outfit', sans-serif";
  ctx.fillText(candidateName || "Candidate", 600, 360);

  // Subtext
  ctx.fillStyle = "#d1d5db";
  ctx.font = "22px 'Inter', sans-serif";
  ctx.fillText(`for successfully completing the examination in`, 600, 430);

  // Quiz Title
  ctx.fillStyle = "#38bdf8";
  ctx.font = "bold 32px 'Outfit', sans-serif";
  ctx.fillText(quizTitle, 600, 480);

  // Score Badge
  ctx.fillStyle = "#10b981";
  ctx.font = "bold 28px 'Inter', sans-serif";
  ctx.fillText(`Scored: ${scorePercentage}% — Distinction & Mastery`, 600, 550);

  // Date and Certificate ID
  ctx.textAlign = "left";
  ctx.fillStyle = "#6b7280";
  ctx.font = "16px 'Inter', sans-serif";
  ctx.fillText(`Date: ${new Date(dateStr || Date.now()).toLocaleDateString()}`, 100, 680);

  ctx.textAlign = "right";
  ctx.fillText(`Credential ID: QUIZ-${Math.random().toString(36).substring(2, 10).toUpperCase()}`, 1100, 680);

  // Download Trigger
  const a = document.createElement("a");
  a.download = `Certificate_${candidateName.replace(/\s+/g, '_')}.png`;
  a.href = canvas.toDataURL("image/png");
  a.click();
}
