import numpy as np
def watering_decision(y_pred1_inv, threshold=2260, rate=0.5):
    """tahminler: ileriye dönük 30 adımlık tahmin dizisi (tek örnek için)"""
    left_below = np.sum(np.array(y_pred1_inv) < threshold)
    if left_below / len(y_pred1_inv) >= rate:
        return True
    return False

def watering_time_expected(y_pred1_inv, threshold, interval_second=60):
    """
    Tahmin edilen nem dizisinden, eşik altına ilk düşüş anını bulur.
    
    Returns:
      süre_saniye: int | None (kaç saniye sonra sulama gerekir)
    """
    for i, val in enumerate(y_pred1_inv):
        if val < threshold:
            return (i+1) * interval_second  # Örn: 4. adımda düşüyorsa = 4*30 = 120 saniye sonra
    return None  # Eşik altına hiç düşmüyorsa, sulama gerekmiyor

