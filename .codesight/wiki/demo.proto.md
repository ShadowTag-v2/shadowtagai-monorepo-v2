# Demo.proto

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Demo.proto subsystem handles **9 routes**.

## Routes

- `RPC` `/CartService/AddItem` → in: AddItemRequest, out: Empty
  `external_repos/apps/microservices-demo/protos/demo.proto`
- `RPC` `/RecommendationService/ListRecommendations` → in: ListRecommendationsRequest, out: ListRecommendationsResponse
  `external_repos/apps/microservices-demo/protos/demo.proto`
- `RPC` `/ProductCatalogService/ListProducts` → in: Empty, out: ListProductsResponse
  `external_repos/apps/microservices-demo/protos/demo.proto`
- `RPC` `/ShippingService/GetQuote` → in: GetQuoteRequest, out: GetQuoteResponse
  `external_repos/apps/microservices-demo/protos/demo.proto`
- `RPC` `/CurrencyService/GetSupportedCurrencies` → in: Empty, out: GetSupportedCurrenciesResponse
  `external_repos/apps/microservices-demo/protos/demo.proto`
- `RPC` `/PaymentService/Charge` → in: ChargeRequest, out: ChargeResponse
  `external_repos/apps/microservices-demo/protos/demo.proto`
- `RPC` `/EmailService/SendOrderConfirmation` → in: SendOrderConfirmationRequest, out: Empty
  `external_repos/apps/microservices-demo/protos/demo.proto`
- `RPC` `/CheckoutService/PlaceOrder` → in: PlaceOrderRequest, out: PlaceOrderResponse
  `external_repos/apps/microservices-demo/protos/demo.proto`
- `RPC` `/AdService/GetAds` → in: AdRequest, out: AdResponse
  `external_repos/apps/microservices-demo/protos/demo.proto`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/apps/microservices-demo/protos/demo.proto`

---
_Back to [overview.md](./overview.md)_