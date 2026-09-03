export async function downloadTextPdf(title: string, subtitle: string, markdown: string) {
  const { jsPDF } = await import('jspdf');
  const pdf = new jsPDF({ unit: 'mm', format: 'a4' });
  const margin = 18;
  const width = 174;
  let y = 20;
  pdf.setFont('helvetica', 'bold');
  pdf.setFontSize(18);
  pdf.text(title, margin, y);
  y += 8;
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(10);
  pdf.setTextColor(90);
  pdf.text(subtitle, margin, y);
  y += 10;
  pdf.setTextColor(25);
  for (const rawLine of markdown.split('\n')) {
    const line = rawLine.replace(/^#{1,6}\s*/, '').replace(/\*\*/g, '').replace(/^[-*]\s+/, '• ');
    const wrapped = pdf.splitTextToSize(line || ' ', width) as string[];
    for (const part of wrapped) {
      if (y > 279) { pdf.addPage(); y = 20; }
      pdf.text(part, margin, y);
      y += 5.2;
    }
    if (!line) y += 2;
  }
  pdf.save(`${title.toLowerCase().replace(/[^a-z0-9]+/gi, '-')}.pdf`);
}
