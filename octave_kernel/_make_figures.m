function _make_figures(plot_dir, fmt, name, wid, hgt, res)
    %%%% Create figures in the given plot directory.
    %%%%

    handles = get(0, 'children');
    for ind = 1:length(handles)
        filename = sprintf('%s%03d', name, ind);
        filepath = fullfile(plot_dir, [filename, '.', fmt]);
        pngpath = fullfile(plot_dir, [filename, '.png']);

        h = handles(ind);
        pos = get(h, 'position');
        % If no width or height is given, use the figure size.
        if (wid < 0 && hgt < 0)
          wid = pos(3);
          hgt = pos(4);
        % If no width is given, scale based on figure aspect.
        elseif (wid < 0)
          wid = pos(3) * hgt / pos(4);
        % If no height is given, scale based on figure aspect.
        elseif (hgt < 0)
          hgt = pos(4) * wid / pos(3);
        end;

        size_opt = sprintf('-S%d,%d', wid, hgt);
        res_opt = sprintf('-r%d', res);

        % Try to use imwrite if the figure only contains an image.
        use_imwrite = false
        try
          grandchild = get(get(h, 'children'), 'children');
          use_imwrite = strcmp(get(grandchild, 'type'), 'image') == 1
        end;

        if (use_imwrite)
            try
                 image = double(get(grandchild, 'cdata'));
                 clim = get(get(h, 'children'), 'clim');
                 image = image - clim(1);
                 image = image ./ (clim(2) - clim(1));
                 % Force a png file.
                 imwrite(uint8(image*255), pngpath);
            catch
               % Fall back on a standard figure save.
               safe_print(h, filepath, pngpath, res_opt, size_opt);
            end;
        else
            safe_print(h, filepath, pngpath, res_opt, size_opt);
        end;
        close(h);
    end;
end;


function safe_print(h, filepath, altpath, res_opt, size_opt) 
  try 
    inner_print(h, filepath, res_opt, size_opt)
  catch
    inner_print(h, altpath, res_opt, size_opt)
  end
end


function inner_print(h, filepath, res_opt, size_opt)
  try
    print(h, filepath, res_opt, size_opt)
  catch
    print(h, filepath)
  end
end
