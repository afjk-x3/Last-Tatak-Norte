import { CartItem, PaymentMethod, DeliveryMethod } from '../types';

/**
 * Sends a notification to Zapier when a new order is created.
 * Only fires for prepaid methods (GCash or Credit/Debit Card).
 * This function is non-blocking and will not crash the app if the request fails.
 */
export const zapierNewOrder = (
  orderId: string,
  customerId: string,
  customerName: string,
  customerEmail: string,
  items: CartItem[],
  totalAmount: number,
  paymentMethod: PaymentMethod,
  deliveryMethod: DeliveryMethod
) => {
  // Only fire for specific payment methods
  if (paymentMethod !== 'GCash' && paymentMethod !== 'Credit/Debit Card' && paymentMethod !== 'COD') {
    return;
  }

  const webhookUrl = import.meta.env.VITE_ZAPIER_NEW_ORDER;

  if (!webhookUrl) {
    console.warn('Zapier Webhook URL is not configured in environment variables.');
    return;
  }

  const itemsSummary = items
    .map(item => {
      const variation = item.selectedVariation?.name || 'Standard';
      const itemTotal = new Intl.NumberFormat('en-PH', {
        style: 'currency',
        currency: 'PHP',
      }).format(item.price * item.quantity);
      return `• ${item.quantity}x ${item.name} (${variation}) - ${itemTotal}`;
    })
    .join('\n');

  const formattedTotal = new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(totalAmount);

  const payload = {
    customerEmail: customerEmail,
    customerName: customerName,
    orderId: orderId,
    customerId: customerId,
    orderTotal: formattedTotal,
    itemsSummary: itemsSummary,
    itemCount: items.length,
    paymentMethod: paymentMethod,
    deliveryMethod: deliveryMethod,
    timestamp: new Date().toISOString(),
    source: 'tataknorte',
  };

  // Perform the request asynchronously (non-blocking)
  fetch(webhookUrl, {
    method: 'POST',
    mode: 'no-cors',
    headers: {
      'Content-Type': 'text/plain',
    },
    body: JSON.stringify(payload),
  })
    .then(() => console.log('Zapier notification sent successfully'))
    .catch((error) => {
      // Non-blocking: we just log the error
      console.error('Failed to send Zapier notification:', error);
    });
};
