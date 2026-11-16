package main

import (
	"io"
	"os"
	"testing"
)

func TestPrintStartup(t *testing.T) {
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatalf("не удалось подготовить перехват вывода: %v", err)
	}
	previous := os.Stdout
	os.Stdout = w
	t.Cleanup(func() {
		os.Stdout = previous
		r.Close()
		w.Close()
	})
	PrintStartup()
	os.Stdout = previous
	w.Close()
	got, err := io.ReadAll(r)
	if err != nil {
		t.Fatalf("не удалось прочитать вывод: %v", err)
	}
	want := "Сервис заказов запущен\nАдрес: http://127.0.0.1:8080\n"
	if string(got) != want {
		t.Fatalf("сообщение о запуске: ждём %q, получили %q", want, string(got))
	}
}
