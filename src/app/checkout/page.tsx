import { CheckoutForm } from './CheckoutForm';

export default function CheckoutPage() {
  // Generate the unique transaction ID securely on the server
  const idempotencyKey = crypto.randomUUID();

  return (
    <div className="max-w-md mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-4">Secure Checkout</h1>
      <CheckoutForm idempotencyKey={idempotencyKey} />
    </div>
  );
}
