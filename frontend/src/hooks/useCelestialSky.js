import { useCallback, useEffect, useMemo, useState } from 'react';
import { sunPosition, moonPosition } from '../lib/astro';

const IP_API = 'https://ipapi.co/json/';
const WEATHER_API = 'https://api.open-meteo.com/v1/forecast';
const DAY = 60 * 1000;
// Stable per-app-session token so location fetching doesn't restage on HMR.
const SESSION_KEY = 0x5a1c3a77;

/** Resolve a location: prefer geolocation, fall back to IP geolocation. */
const getLocation = () =>
  new Promise((resolve) => {
    const done = (lat, lon, source) => resolve({ lat, lon, source });
    if (typeof navigator !== 'undefined' && 'geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => done(pos.coords.latitude, pos.coords.longitude, 'gps'),
        async () => {
          try {
            const res = await fetch(IP_API);
            const d = await res.json();
            if (d && d.latitude && d.longitude) done(d.latitude, d.longitude, 'ip');
            else done(28.6139, 77.209, 'fallback');
          } catch {
            done(28.6139, 77.209, 'fallback');
          }
        },
        { timeout: 8000, maximumAge: 600000 }
      );
    } else {
      fetch(IP_API)
        .then((r) => r.json())
        .then((d) =>
          d && d.latitude && d.longitude
            ? done(d.latitude, d.longitude, 'ip')
            : done(28.6139, 77.209, 'fallback')
        )
        .catch(() => done(28.6139, 77.209, 'fallback'));
    }
  });

/** Current conditions from Open-Meteo (free, no key). */
const fetchWeather = async (lat, lon) => {
  const params = new URLSearchParams({
    latitude: lat,
    longitude: lon,
    current: 'cloud_cover,precipitation,rain,showers,snowfall,weather_code,is_day,wind_speed_10m',
  });
  const res = await fetch(`${WEATHER_API}?${params}`);
  if (!res.ok) throw new Error('weather fetch failed');
  const json = await res.json();
  return json.current || null;
};

/** Map compass azimuth to a screen X (0..1), given the device heading. */
export const azToX = (azimuth, heading) => {
  const rel = ((azimuth - heading + 540) % 360) - 180; // -180..180, 0 = straight ahead
  // Straight ahead = 0.5 (centre), to the right = towards 1.0.
  return (rel / 180) * 0.5 + 0.5;
};

/**
 * Everything the sky needs, derived from the observer's real place and time:
 * location, live weather, solar/lunar positions, and (optionally) the
 * device compass heading.
 */
const useCelestialSky = () => {
  const [location, setLocation] = useState(null);
  const [locSource, setLocSource] = useState('ip');
  const [weather, setWeather] = useState(null);
  const [now, setNow] = useState(() => new Date());
  const [heading, setHeading] = useState(0);
  const [headingSupported, setHeadingSupported] = useState(false);
  const [headingActive, setHeadingActive] = useState(false);
  const [permissionRequested, setPermissionRequested] = useState(false);

  // Lock location/weather to a "page session" so it doesn't churn mid-browse.
  const sessionKey = SESSION_KEY;

  useEffect(() => {
    let cancelled = false;
    getLocation().then((loc) => {
      if (cancelled) return;
      setLocation(loc);
      setLocSource(loc.source);
    });
    return () => {
      cancelled = true;
    };
  }, [sessionKey]);

  // Fetch weather when the location lands, then refresh hourly.
  useEffect(() => {
    if (!location) return;
    let cancelled = false;
    const load = () =>
      fetchWeather(location.lat, location.lon)
        .then((w) => {
          if (!cancelled && w) setWeather(w);
        })
        .catch(() => {});
    load();
    const id = setInterval(load, 60 * 60 * 1000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [location, sessionKey]);

  // Advance the clock every minute so the sun/moon track real motion.
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), DAY);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (typeof DeviceOrientationEvent === 'undefined' || !('requestPermission' in DeviceOrientationEvent)) {
      return;
    }
    DeviceOrientationEvent.requestPermission()
      .then((state) => {
        if (state === 'granted') {
          setHeadingSupported(true);
          setHeadingActive(true);
        }
      })
      .catch(() => {});
  }, []);

  // Device orientation: which way the device is facing, used to place the sun
  // and moon horizontally against the real horizon.
  useEffect(() => {
    const onOrientation = (e) => {
      if (typeof e.webkitCompassHeading === 'number') {
        setHeading(e.webkitCompassHeading);
        setHeadingActive(true);
      } else if (typeof e.alpha === 'number') {
        setHeading((360 - e.alpha) % 360);
        setHeadingActive(true);
      }
    };
    window.addEventListener('deviceorientation', onOrientation, true);
    return () => window.removeEventListener('deviceorientation', onOrientation, true);
  }, []);

  const { lat: latitude, lon: longitude } = location || { lat: null, lon: null };

  const celestial = useMemo(() => {
    if (latitude == null || longitude == null) return null;
    const sun = sunPosition(now, latitude, longitude);
    const moon = moonPosition(now, latitude, longitude);
    return { sun, moon, now, weather };
  }, [latitude, longitude, now, weather]);

  const requestHeading = useCallback(() => {
    if (typeof DeviceOrientationEvent !== 'undefined' && 'requestPermission' in DeviceOrientationEvent) {
      setPermissionRequested(true);
      DeviceOrientationEvent.requestPermission()
        .then((state) => {
          if (state === 'granted') {
            setHeadingSupported(true);
            setHeadingActive(true);
          }
        })
        .catch(() => {});
    } else if (typeof DeviceOrientationEvent !== 'undefined') {
      setHeadingSupported(true);
      setHeadingActive(true);
    }
  }, []);

  return {
    location,
    locSource,
    weather,
    celestial,
    heading,
    headingSupported,
    headingActive,
    requestHeading,
    permissionRequested,
  };
};

export default useCelestialSky;