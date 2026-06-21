function generateKey() {
  return "sk_" + Math.random().toString(36).substring(2, 18);
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({
      message: "Method not allowed"
    });
  }

  const key = generateKey();

  return res.status(200).json({
    success: true,
    key,
    note: "Store this in a database for production."
  });
}
