/**
 * Solar and lunar position math. Pure functions, no network.
 *
 * Solar ephemeris: the classic NOAA/Spencer calculation, accurate to a few
 * arcminutes, sufficient to place the sun and moon on screen.
 *
 * Lunar ephemeris: simplified but solid low-precision algorithm (2807 sunrise
 * tables style) — good to <0.5 deg, plenty for a sky map.
 *
 * Angles: functions return degrees. Azimuth is compass-style:
 *   0 = north, 90 = east, 180 = south, 270 = west.
 * Elevation: 90 = zenith, 0 = horizon, negative = below horizon.
 */

export const DEG = Math.PI / 180;
export const RAD = 180 / Math.PI;

const normalizeDeg = (d) => ((d % 360) + 360) % 360;
const normalizeSigned = (d) => ((d + 180) % 360) - 180;

/** Julian Day from a Date. */
export const toJulian = (date) => date.getTime() / 86400000 + 2440587.5;

/** Sun geocentric ecliptic longitude + mean obliquity at a Julian day. */
const sunGeometry = (jd) => {
  const T = (jd - 2451545.0) / 36525; // centuries from J2000
  const L0 = 280.46646 + T * (36000.76983 + 0.0003032 * T); // mean longitude
  const M = 357.52911 + T * (35999.05029 - 0.0001537 * T); // mean anomaly
  const C =
    Math.sin(M * DEG) * (1.914602 - T * (0.004817 + 0.000014 * T)) +
    Math.sin(2 * M * DEG) * (0.019993 - 0.000101 * T) +
    Math.sin(3 * M * DEG) * 0.000289;
  const trueLong = normalizeDeg(L0 + C);
  const apparent = trueLong - 0.00569 - 0.00478 * Math.sin((125.04 - 1934.136 * T) * DEG);
  // Mean obliquity of the ecliptic, in degrees
  const omega = 23.43929111 - T * (46.815 + T * (0.00059 - T * 0.001813)) / 3600;
  const obliquity = omega + 0.00256 * Math.cos((125.04 - 1934.136 * T) * DEG);
  return { longitude: apparent, obliquity };
};

/** Convert geographic lat + equatorial (RA, dec) + hour angle to local horizon coords. */
const toHorizon = (lat, decl, hourAngle) => {
  const latR = lat * DEG;
  const decR = decl * DEG;
  const hR = hourAngle * DEG;
  const sinAlt =
    Math.sin(latR) * Math.sin(decR) +
    Math.cos(latR) * Math.cos(decR) * Math.cos(hR);
  const elevation = Math.asin(sinAlt) * RAD;
  const cosAz =
    (Math.sin(decR) - Math.sin(latR) * sinAlt) /
    (Math.cos(latR) * Math.cos(elevation * DEG) || 1e-9);
  const az = normalizeDeg(Math.acos(Math.max(-1, Math.min(1, cosAz))) * RAD);
  // Hour angle > 0 means the body is west of the local meridian
  return { elevation, azimuth: hourAngle > 0 ? Math.round((360 - az) * 10) / 10 : Math.round(az * 10) / 10 };
};

/** Greenwich mean sidereal time in degrees. */
const gmstDeg = (jd) => normalizeDeg(280.46061837 + 360.98564736629 * (jd - 2451545.0));

/**
 * Sun horizontal coordinates (elevation°, azimuth°) for a Date + observer.
 */
export const sunPosition = (date, lat, lon) => {
  const jd = toJulian(date);
  const { longitude, obliquity } = sunGeometry(jd);
  // Right ascension and declination of the sun
  const ra = normalizeDeg(Math.atan2(Math.cos(obliquity * DEG) * Math.sin(longitude * DEG), Math.cos(longitude * DEG)) * RAD);
  const decl = Math.asin(Math.sin(obliquity * DEG) * Math.sin(longitude * DEG)) * RAD;
  const hourAngle = normalizeSigned(gmstDeg(jd) + lon - ra);
  return toHorizon(lat, decl, hourAngle);
};

/**
 * Moon horizontal coordinates (elevation°, azimuth°) + illuminated fraction.
 */
export const moonPosition = (date, lat, lon) => {
  const jd = toJulian(date);
  const D = jd - 2451545.0;

  // Low-precision lunar position (good to <0.5 deg for display purposes)
  const N = normalizeDeg(125.1228 - 0.0529538083 * D); // longitude of ascending node
  const L = normalizeDeg(218.316 + 13.176396 * D); // mean longitude
  const M = normalizeDeg(134.963 + 13.064993 * D); // mean anomaly
  const F = normalizeDeg(93.272 + 13.229350 * D); // argument of latitude

  const lngEcl = normalizeDeg(
    L +
    6.289 * Math.sin(M * DEG) +
    1.274 * Math.sin((2 * L - M) * DEG) +
    0.658 * Math.sin(2 * L * DEG) +
    0.214 * Math.sin(2 * M * DEG) -
    0.114 * Math.sin(F * DEG)
  );
  const latEcl =
    5.128 * Math.sin(F * DEG) +
    0.280 * Math.sin((M + F) * DEG) +
    0.277 * Math.sin((M - F) * DEG) +
    0.173 * Math.sin((2 * L - F) * DEG);

  const T = (jd - 2451545.0) / 36525;
  const obliquity = 23.43929111 - T * (46.815 + T * (0.00059 - T * 0.001813)) / 3600;

  // Ecliptic -> equatorial
  const le = lngEcl * DEG;
  const be = latEcl * DEG;
  const ep = obliquity * DEG;
  const ra = normalizeDeg(Math.atan2(Math.sin(le) * Math.cos(ep) - Math.tan(be) * Math.sin(ep), Math.cos(le)) * RAD);
  const decl = Math.asin(Math.sin(be) * Math.cos(ep) + Math.cos(be) * Math.sin(ep) * Math.sin(le)) * RAD;

  const hourAngle = normalizeSigned(gmstDeg(jd) + lon - ra);
  const horiz = toHorizon(lat, decl, hourAngle);

  // Illuminated fraction from the sun–moon geocentric elongation
  const sunLng = sunGeometry(jd).longitude;
  const elongation = Math.acos(
    Math.max(-1, Math.min(1, Math.cos(be) * Math.cos((sunLng - lngEcl) * DEG)))
  ) * RAD;
  const illuminated = (1 - Math.cos(elongation * DEG)) / 2;

  return { ...horiz, illuminated };
};