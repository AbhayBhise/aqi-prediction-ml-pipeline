import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Cloud, CloudRain, Sun, Moon, Star, Wind, MapPin, Loader2, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import useThemeStore from '../store/useThemeStore';
import useDashboardStore from '../store/useDashboardStore';
import LoadingOverlay from '../components/LoadingOverlay';

const Dashboard = () => {
  const {
    dashboardData, setDashboardData,
    weatherData, setWeatherData,
    location, setLocation,
    loading, setLoading,
    error, setError
  } = useDashboardStore();

  const [permissionDenied, setPermissionDenied] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const theme = useThemeStore((s) => s.theme);
  const isDayTime = theme === 'light';

  useEffect(() => {
    if (!dashboardData && !loading) {
      fetchDashboardData();
    }
    if (!weatherData && !loading) {
      fetchLocationAndWeather();
    }
  }, []);

  useEffect(() => {
    let interval;
    if (loading && !dashboardData) {
      setProgress(0);
      interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) return prev;
          return prev + Math.floor(Math.random() * 5) + 1;
        });
      }, 150);
    } else if (dashboardData) {
      setProgress(100);
      if (interval) clearInterval(interval);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loading, dashboardData]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const res = await api.get('/eda_data');
      setDashboardData(res.data || []);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch dashboard data');
      setDashboardData([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchLocationAndWeather = async () => {
    try {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            setLocation({ lat, lon });
            await fetchWeather(lat, lon, null);
          },
          async (error) => {
            console.warn("Geolocation denied or error. Falling back to IP geolocation.", error);
            try {
              const geoRes = await fetch('https://ipapi.co/json/');
              const geoData = await geoRes.json();
              if(geoData && geoData.latitude && geoData.longitude) {
                const lat = parseFloat(geoData.latitude);
                const lon = parseFloat(geoData.longitude);
                setLocation({ lat, lon });
                await fetchWeather(lat, lon, geoData.city);
              } else {
                throw new Error("Invalid IP API response");
              }
            } catch (err) {
              setPermissionDenied(true);
              const defaultLat = 28.6139;
              const defaultLon = 77.2090;
              setLocation({ lat: defaultLat, lon: defaultLon });
              await fetchWeather(defaultLat, defaultLon, "New Delhi");
            }
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
      } else {
        const defaultLat = 28.6139;
        const defaultLon = 77.2090;
        setLocation({ lat: defaultLat, lon: defaultLon });
        fetchWeather(defaultLat, defaultLon, "New Delhi");
      }
    } catch(e) {
      console.error(e);
    }
  };

  const fetchWeather = async (lat, lon, preFetchedCity) => {
    try {
      const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m`);
      const data = await res.json();
      
      let cityName = preFetchedCity;
      if (!cityName) {
        try {
          const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
          const geoData = await geoRes.json();
          cityName = geoData.address.city || geoData.address.town || geoData.address.village || geoData.address.county || "Your Location";
        } catch (e) {
          console.error("Reverse geocoding failed", e);
          cityName = "Your Location";
        }
      }

      setWeatherData({
        ...data.current_weather,
        city: cityName,
        humidity: data.hourly.relative_humidity_2m[0] // approximation for current hour
      });
    } catch (err) {
      console.error("Failed to fetch weather", err);
    }
  };

  const chartData = (dashboardData && dashboardData.aqi_distribution) 
    ? Object.keys(dashboardData.aqi_distribution).map(key => ({
        name: key,
        count: dashboardData.aqi_distribution[key]
      })) 
    : [];

  const getWeatherIcon = (weathercode) => {
    if (weathercode === undefined) return <Sun className="w-12 h-12 text-yellow-400" />;
    if (weathercode <= 3) return <Sun className="w-12 h-12 text-yellow-400" />;
    if (weathercode >= 45 && weathercode <= 48) return <Cloud className="w-12 h-12 text-slate-400" />;
    if (weathercode >= 51 && weathercode <= 67) return <CloudRain className="w-12 h-12 text-blue-400" />;
    if (weathercode >= 71 && weathercode <= 77) return <Cloud className="w-12 h-12 text-slate-200" />;
    if (weathercode >= 80 && weathercode <= 82) return <CloudRain className="w-12 h-12 text-blue-500" />;
    if (weathercode >= 95) return <Wind className="w-12 h-12 text-indigo-400" />;
    return <Sun className="w-12 h-12 text-yellow-400" />;
  };

  return (
    <div className="pb-8 min-h-screen relative overflow-hidden bg-transparent">
      

      <div className="relative z-10 px-6 pt-6">
        <h1 className={`text-3xl font-bold mb-8 transition-colors duration-1000 `}>Dashboard Overview</h1>

        {loading && !dashboardData ? (
          <LoadingOverlay message="Loading data..." progress={progress} />
        ) : (
          <>
            {/* Top Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className={`backdrop-blur-md border rounded-xl p-6 bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl `}>
                <p className={` text-sm font-medium`}>Dataset Rows</p>
                <h2 className={`text-3xl font-bold mt-2 `}>842,160</h2>
              </div>
              <div className={`backdrop-blur-md border rounded-xl p-6 bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl `}>
                <p className={` text-sm font-medium`}>Features</p>
                <h2 className={`text-3xl font-bold mt-2 `}>71</h2>
              </div>
              <div className={`backdrop-blur-md border rounded-xl p-6 bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl `}>
                <p className={` text-sm font-medium`}>ML Models Trained</p>
                <h2 className={`text-3xl font-bold mt-2 `}>10</h2>
              </div>
              
              {/* Live Weather Card */}
              <div className={`backdrop-blur-md border rounded-xl p-6 bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl relative overflow-hidden `}>
                <div className="absolute top-0 right-0 -mt-4 -mr-4 opacity-10 text-slate-800">
                  <Wind className="w-32 h-32" />
                </div>
                <div className="flex justify-between items-start">
                  <div>
                    <p className={` text-sm font-medium flex items-center`}>
                      <MapPin className="w-3 h-3 mr-1" />
                      {weatherData ? weatherData.city : 'Locating...'}
                    </p>
                    <div className="flex items-center mt-2">
                      <h2 className={`text-3xl font-bold mr-3 `}>
                        {weatherData ? `${weatherData.temperature}Â°C` : '--Â°C'}
                      </h2>
                    </div>
                    <p className={` text-xs mt-2`}>
                      {weatherData ? `Wind: ${weatherData.windspeed} km/h | Hum: ${weatherData.humidity}%` : 'Loading weather...'}
                    </p>
                  </div>
                  <motion.div 
                    animate={{ y: [0, -5, 0] }} 
                    transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
                  >
                    {weatherData ? getWeatherIcon(weatherData.weathercode) : <Loader2 className={`w-8 h-8 animate-spin `} />}
                  </motion.div>
                </div>
                {permissionDenied && (
                  <p className="text-xs text-amber-600 mt-2 font-medium">Using default location (IP restricted).</p>
                )}
              </div>
            </div>

            {/* Insights Section: System Limitations & Daily Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              <div className={`lg:col-span-2 backdrop-blur-md border rounded-xl p-6 bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl `}>
                <div className="flex items-center mb-6">
                  <BookOpen className={`w-5 h-5 mr-2 `} />
                  <h3 className={`text-lg font-semibold `}>System Limitations & Optimal Solutions</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className={`font-medium mb-3 flex items-center `}>
                      <span className="w-2 h-2 rounded-full bg-red-400 mr-2"></span>
                      Current System Drawbacks
                    </h4>
                    <ul className="space-y-3">
                      <li className={`text-sm `}>
                        <strong className={``}>Sparse Sensor Networks:</strong> Ground-level monitoring stations are expensive and unevenly distributed, leading to spatial gaps in AQI predictions.
                      </li>
                      <li className={`text-sm `}>
                        <strong className={``}>Temporal Lag:</strong> Traditional stationary sensors often report data with a 1-2 hour delay, making real-time intervention difficult.
                      </li>
                      <li className={`text-sm `}>
                        <strong className={``}>Single-Modal Data:</strong> Relying purely on historical tabular data ignores complex meteorological dispersion patterns and urban topography.
                      </li>
                    </ul>
                  </div>

                  <div>
                    <h4 className={`font-medium mb-3 flex items-center `}>
                      <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2"></span>
                      Research-Backed Optimal Solutions
                    </h4>
                    <ul className="space-y-3">
                      <li className={`text-sm `}>
                        <strong className={``}>Satellite Imagery Integration:</strong> Implementing multi-modal deep learning (e.g., CNNs on Sentinel-5P satellite data) alongside ground sensors provides high-resolution spatial coverage (Source: Zheng et al., 2021).
                      </li>
                      <li className={`text-sm `}>
                        <strong className={``}>Mobile Edge-IoT Sensors:</strong> Deploying low-cost sensors on public transport creates dynamic, real-time spatial mapping at a fraction of traditional costs.
                      </li>
                      <li className={`text-sm `}>
                        <strong className={``}>Graph Neural Networks (GNNs):</strong> Modeling monitoring stations as graph nodes captures spatial-temporal dependencies and wind propagation effects much better than LSTMs alone.
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Daily Summary & Alerts */}
              <div className={`backdrop-blur-md border rounded-xl p-6 bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl flex flex-col bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl `}>
                <h3 className={`text-lg font-semibold mb-4 `}>Daily Summary</h3>
                
                <div className={`border rounded-lg p-4 mb-6 `}>
                  <div className="flex items-start">
                    <div className={`p-2 rounded-full mr-3 shrink-0 `}>
                      <Wind className={`w-4 h-4 `} />
                    </div>
                    <div>
                      <h4 className={`font-medium text-sm mb-1 `}>Local Air Quality Alert</h4>
                      <p className={`text-sm leading-relaxed `}>
                        Air quality is poor today, with a peak of Very Unhealthy expected around 11 AM. Reduce prolonged outdoor exertion.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex-1 space-y-4">
                  <div className={`flex justify-between items-center border-b pb-3 `}>
                    <span className={`text-sm `}>Primary Pollutant</span>
                    <span className={`font-medium text-sm `}>PM2.5</span>
                  </div>
                  <div className={`flex justify-between items-center border-b pb-3 `}>
                    <span className={`text-sm `}>Avg Temperature</span>
                    <span className={`font-medium text-sm `}>24Â°C</span>
                  </div>
                  <div className="flex justify-between items-center pb-3">
                    <span className={`text-sm `}>Status</span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border `}>
                      Sensors Online
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Forecast Bar Graph (At the Bottom) */}
            <div className={`backdrop-blur-md border rounded-xl p-6 bg-white/10 border-white/20 dark:bg-slate-900/40 dark:border-slate-800 shadow-xl mb-8 `}>
              <div className="flex justify-between items-center mb-6">
                <h3 className={`text-lg font-semibold `}>Aggregate AQI Category Distribution</h3>
                <span className={`px-3 py-1 text-xs font-medium rounded-full border `}>
                  Global Dataset
                </span>
              </div>
              <div className="w-full h-[300px]">
                {chartData && chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={isDayTime ? '#cbd5e1' : '#334155'} vertical={false} />
                      <XAxis dataKey="name" stroke={isDayTime ? '#475569' : '#94a3b8'} tick={{fontSize: 12}} />
                      <YAxis stroke={isDayTime ? '#475569' : '#94a3b8'} tick={{fontSize: 12}} />
                      <Tooltip 
                        cursor={{fill: isDayTime ? '#f1f5f9' : '#1e293b'}} 
                        contentStyle={{backgroundColor: isDayTime ? '#ffffff' : '#0f172a', borderColor: isDayTime ? '#e2e8f0' : '#334155', color: isDayTime ? '#0f172a' : '#f8fafc', borderRadius: '0.5rem'}} 
                        itemStyle={{color: isDayTime ? '#4f46e5' : '#818cf8'}}
                      />
                      <Bar dataKey="count" fill={isDayTime ? '#3b82f6' : '#6366f1'} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className={`flex items-center justify-center h-full `}>
                    Loading distribution data...
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

