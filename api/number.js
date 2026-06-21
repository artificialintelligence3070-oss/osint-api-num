const KEYS = [
  {
    key: "demo123",
    name: "Admin",
    dailyLimit: 1000,
    expiry: "2027-01-01"
  }
];

export default async function handler(req, res) {
  try {
    const { key, num } = req.query;

    if (!key) {
      return res.status(401).json({
        success: false,
        message: "API key required"
      });
    }

    const user = KEYS.find(k => k.key === key);

    if (!user) {
      return res.status(403).json({
        success: false,
        message: "Invalid API key"
      });
    }

    if (new Date(user.expiry) < new Date()) {
      return res.status(403).json({
        success: false,
        message: "API key expired"
      });
    }

    const response = await fetch(
      `https://ft-osint-api.duckdns.org/api/number?key=ft-rahun2m&num=${encodeURIComponent(num)}`
    );

    const data = await response.json();

    return res.status(200).json({
      owner: user.name,
      data
    });

  } catch (err) {
    return res.status(500).json({
      success: false,
      error: err.message
    });
  }
}
