import React, { useState, useEffect } from 'react';
import { Coffee, X } from 'lucide-react';

const BuyMeACoffeeModal = () => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Check if user has already dismissed or interacted with it recently
    const hasSeenModal = localStorage.getItem('hasSeenCoffeeModal');

    if (hasSeenModal) return;

    let clickCount = 0;

    const handleUserInteraction = () => {
      clickCount++;
      // Show modal after 8 interactions (clicks/exploring)
      if (clickCount === 8) {
        // Wait 1.5 seconds after the 8th click so it doesn't abruptly interrupt the user
        setTimeout(() => {
          setIsOpen(true);
        }, 1500);

        // Remove listener once triggered
        window.removeEventListener('click', handleUserInteraction);
      }
    };

    window.addEventListener('click', handleUserInteraction);

    return () => {
      window.removeEventListener('click', handleUserInteraction);
    };
  }, []);

  const handleClose = () => {
    setIsOpen(false);
    // Don't show again once closed
    localStorage.setItem('hasSeenCoffeeModal', 'true');
  };

  const handleSupport = () => {
    setIsOpen(false);
    localStorage.setItem('hasSeenCoffeeModal', 'true');
    window.open('https://buymeacoffee.com/bhiseabhayq', '_blank');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-sm w-full shadow-2xl relative animate-in zoom-in-95 duration-300">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X size={20} />
        </button>

        <div className="flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-[#FFDD00]/10 rounded-full flex items-center justify-center mb-4 border border-[#FFDD00]/20">
            <Coffee size={32} className="text-[#FFDD00]" />
          </div>

          <h2 className="text-xl font-bold text-white mb-2">Finding this useful?</h2>
          <p className="text-slate-400 text-sm mb-6">
            If this project has helped you, consider supporting the development. It keeps the coffee flowing and the code shipping!
          </p>

          <button
            onClick={handleSupport}
            className="w-full flex items-center justify-center mb-2 hover:scale-105 transition-transform duration-200"
          >
            <img
              src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
              alt="Buy Me A Coffee"
              className="h-[50px] w-auto rounded-lg shadow-md"
            />
          </button>

          <button
            onClick={handleClose}
            className="mt-3 text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            Maybe later
          </button>
        </div>
      </div>
    </div>
  );
};

export default BuyMeACoffeeModal;
