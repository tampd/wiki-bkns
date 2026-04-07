# BKNS Wiki Skeleton

Bộ skeleton này được dựng theo brief wiki bạn cung cấp và mô phỏng theo kiến trúc public hiện có của bkns.vn.

## Gói bàn giao
- `wiki/`: skeleton để dev thảo luận schema, router và component
- `wiki/_templates/`: template tái sử dụng
- `SITE-NOTES.md`: ghi chú nghiên cứu bố cục / kiến trúc sản phẩm
- `FILE_TREE.txt`: cây thư mục đầy đủ
- `../bkns_wiki_blueprint.md`: bản tóm tắt để chốt với đội code

## Tình trạng hoàn thiện
### Đã điền chi tiết toàn bộ 9 sub-pages + product pages mẫu
- `hosting`
- `vps`
- `ssl`

### Đã tạo đủ file với placeholder an toàn
- `email`
- `ten-mien`
- `server`
- `software`
- `other`
- `uncategorized`

## Ghi chú quan trọng
- Các dữ liệu giá / specs trong 3 category chi tiết chỉ lấy từ public pages đã đọc; chỗ nào chưa đủ dữ liệu đều để `⏳ Đang cập nhật`.
- Skeleton này ưu tiên tính đúng cấu trúc và an toàn dữ liệu hơn là “điền cho đầy”.
- Một số field công ty / hotline / giá SSL đang có dấu hiệu mâu thuẫn giữa các trang public, vì vậy nên bổ sung lớp `verification_status` ở pipeline dù frontmatter public vẫn giữ nguyên.
