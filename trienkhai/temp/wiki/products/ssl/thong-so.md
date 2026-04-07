---
page_id: wiki.products.ssl.thong-so
title: "Chứng Chỉ SSL BKNS — Thông số kỹ thuật"
category: products/ssl
updated: '2026-04-07'
review_state: drafted
claims_used: 14
---


# Chứng Chỉ SSL BKNS — Thông số kỹ thuật

## Bảng specs chuẩn
| Sản phẩm | Giá | Xác thực | Số domain | SAN | Thanh xanh | Bảo hiểm | Trust | Thời hạn | Hỗ trợ | Reissue |
|---|---|---|---|---|---|---|---|---|---|---|
| Positive SSL | 159.000đ/năm | DV | 1 | Không | Không | $10.000 | Standard | 1 năm | 24/7 | 199 ngày |
| Positive SSL Multi-domain | 950.000đ/năm | DV | 3-100 | Có, 259.000đ/domain/năm | Không | $10.000 | Standard | 1 năm | 24/7 | 199 ngày |
| Positive SSL Wildcard | 1.900.000đ/năm | DV | 1 + all subdomain | Không | Không | $10.000 | Standard | 1 năm | 24/7 | 199 ngày |
| InstantSSL Pro | 1.620.000đ/năm | OV | 1 | Không | Không | $10.000 | High | 1 năm | 24/7 | 199 ngày |
| Comodo SSL UCC OV | 2.250.000đ/năm | OV | 3 | Có | Không | $250.000 | High | 1 năm | 24/7 | 199 ngày |
| Comodo Multi-domain SSL | 3.250.000đ/năm | OV | 3-100 | Có, 925.000đ/domain/năm | Không | $250.000 | High | 1 năm | 24/7 | 199 ngày |
| Comodo EV SSL | 5.782.000đ/năm | EV* | 1 | Không | Có | $1.750.000 | Highest | 1 năm | 24/7 | 199 ngày |
| Premium SSL Wildcard | 5.088.000đ/năm | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 1 năm | 24/7 | 199 ngày |
| Comodo EV Multi Domain SSL | ⏳ Đang cập nhật | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| GeoTrust SSL | ⏳ Đang cập nhật | DV/OV/EV | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| DigiCert SSL | ⏳ Đang cập nhật | DV/OV/EV | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Code Signing | ⏳ Đang cập nhật | OV/EV | ⏳ | SAN/N/A | N/A | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

## Trường dữ liệu nên có trong schema
- `brand`
- `validation_level`
- `protected_domains`
- `wildcard_supported`
- `san_supported`
- `insurance_amount`
- `trust_level`
- `term_years`
- `support_window`
- `reissue_days`

## Quy tắc compile
- Giá gia hạn nên tách riêng khỏi giá khởi tạo / phí duy trì
- Dòng Code Signing cần schema khác với SSL website
- Các trường `green_bar`, `insurance_amount`, `trust_level` phải cho phép null

## Sản phẩm liên quan

- [Bảng giá SSL](./bang-gia.md)
- [So sánh SSL](./so-sanh.md)
- [Hướng dẫn SSL](./huong-dan.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)
