import pytest
from cultura.mak_curatoria.diagnostico_proyectos import dir_is_generated, clean_anchor_dir, frame_like


class TestDirIsGenerated:
    def test_direct_match_in_generated_set(self):
        assert dir_is_generated("renders") is True

    def test_normal_project_name_returns_false(self):
        assert dir_is_generated("MiProyecto") is False

    def test_uppercase_renders_still_true(self):
        assert dir_is_generated("RENDERS") is True

    def test_case_variation_of_generated_dir_is_true(self):
        assert dir_is_generated("Renders") is True

    def test_accented_variant_normalizes_to_same_value(self):
        assert dir_is_generated("rénders") is True

    def test_almacenamiento_automatico_base_is_true(self):
        assert dir_is_generated("almacenamiento automatico de adobe after effects") is True

    def test_almacenamiento_automatico_with_suffix_is_true(self):
        assert dir_is_generated("almacenamiento automatico de adobe after effects x") is True

    def test_generated_word_inside_longer_name_is_false(self):
        assert dir_is_generated("my_renders_project") is False


class TestCleanAnchorDir:
    def test_removes_single_trailing_generated_dir(self):
        result = clean_anchor_dir(["ProyectoReal", "renders"])
        assert result == ("ProyectoReal",)

    def test_removes_multiple_trailing_generated_dirs(self):
        result = clean_anchor_dir(["ProyectoReal", "renders", "cache", "backup"])
        assert result == ("ProyectoReal",)

    def test_keeps_last_real_dir_when_trailing_generated(self):
        result = clean_anchor_dir(["Repo", "source", "textures", "renders"])
        assert result == ("Repo",)

    def test_does_not_remove_if_last_is_not_generated(self):
        result = clean_anchor_dir(["ProyectoReal", "assets", "FinalArt"])
        assert result == ("ProyectoReal", "assets", "FinalArt")

    def test_all_dirs_generated_stops_at_one_remaining(self):
        # while len(parts) > 1: nunca reduce a menos de 1 elemento,
        # aunque ese ultimo elemento tambien sea "generado".
        result = clean_anchor_dir(["renders", "cache", "backup"])
        assert result == ("renders",)

    def test_empty_parts_returns_root(self):
        result = clean_anchor_dir([])
        assert result == ("[root]",)

    def test_only_one_dir_and_it_is_generated_keeps_it(self):
        result = clean_anchor_dir(["renders"])
        assert result == ("renders",)

    def test_only_one_dir_and_not_generated_keeps_it(self):
        result = clean_anchor_dir(["MiProyecto"])
        assert result == ("MiProyecto",)

    def test_ignores_generated_in_middle_of_path(self):
        result = clean_anchor_dir(["Repo", "renders", "FinalArt"])
        assert result == ("Repo", "renders", "FinalArt")


class TestFrameLike:
    def test_purely_numeric_string_returns_true(self):
        assert frame_like("0042") is True

    def test_trailing_underscore_number_suffix_returns_true(self):
        assert frame_like("shot_042") is True

    def test_trailing_dash_number_suffix_returns_true(self):
        assert frame_like("comp-99") is True

    def test_word_frame_in_stem_returns_true(self):
        assert frame_like("my_frame_shot") is True

    def test_word_render_in_stem_returns_true(self):
        assert frame_like("render_pass") is True

    def test_word_output_in_stem_returns_true(self):
        assert frame_like("final_output_v01") is True

    def test_word_img_in_stem_returns_true(self):
        assert frame_like("beauty_img") is True

    def test_word_image_in_stem_returns_true(self):
        assert frame_like("plate_image") is True

    def test_word_comp_in_stem_returns_true(self):
        assert frame_like("final_comp") is True

    def test_normal_project_stem_returns_false(self):
        assert frame_like("MiProyecto") is False

    def test_short_number_suffix_returns_false(self):
        assert frame_like("shot_4") is False

    def test_single_digit_returns_true(self):
        assert frame_like("7") is True
