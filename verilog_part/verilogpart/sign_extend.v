module sign_extend (
    input [15:0] in,
    output [15:0] out
);

    // Instruction içindeki immediate zaten 16-bit.
    // 32-bit instruction formatı: Op(6) | Rs(5) | Rx(5) | Imm(16)
    // Veri yolu 16-bit olduğu için genişletme (extension) yapmaya gerek yok,
    // sadece kablo bağlantısı (wire) olarak çalışır.
    assign out = in;

endmodule
